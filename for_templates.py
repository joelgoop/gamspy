import copy

def isnumber(val):
    try:
        float(val)
    except (ValueError,TypeError):
        return False
    return True

class GamsArithmeticElement(object):
    """Gams elements that can be added, subtracted, multiplied and divided to create expressions."""
    def __init__(self,parenthesis=False):
        super(GamsArithmeticElement,self).__init__()
        self.parenthesis = parenthesis


    def __add__(self,other):
        if not (isinstance(other,GamsArithmeticElement) or isnumber(other)):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('+',self,other)
    def __sub__(self,other):
        if isnumber(other):
            return GamsExpression('-',self,other)
        if not isinstance(other,GamsArithmeticElement):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('-',self,other.parenthesized())
    def __div__(self,other):
        if isnumber(other):
            return GamsExpression('/',self.parenthesized(),other)
        if not isinstance(other,GamsArithmeticElement):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('/',self.parenthesized(),other.parenthesized())
    def __mul__(self,other):
        if isnumber(other):
            return GamsExpression('*',self.parenthesized(),other)
        if not isinstance(other,GamsArithmeticElement):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('*',self.parenthesized(),other.parenthesized())

    def __radd__(self,other):
        return GamsExpression(str(other))+self
    def __rsub__(self,other):
        return GamsExpression(str(other))-self
    def __rmul__(self,other):
        return GamsExpression(str(other))*self
    def __rdiv__(self,other):
        return GamsExpression(str(other))/self

    def parenthesized(self):
        new_element = copy.copy(self)
        new_element.parenthesis = True
        return new_element


class GamsElement(object):
    """Gams elements such as a set or parameter"""
    def __init__(self, name, indices=None):
        super(GamsElement, self).__init__()
        self.name = name
        self.indices = indices

    def __str__(self):
        indices_str = '({})'.format(','.join([index.name for index in self.indices])) if self.indices is not None else ''
        return self.name + indices_str


class GamsVariable(GamsElement,GamsArithmeticElement):
    """A variable in GAMS"""
    def __init__(self, name, indices=None):
        super(GamsVariable, self).__init__(name,indices)


class GamsDataElement(GamsElement):
    """A Gams element that can contain data"""
    def __init__(self, name, data=None, indices=None):
        super(GamsDataElement, self).__init__(name,indices)
        self.data = data


class GamsSet(GamsDataElement):
    """A set in GAMS"""
    def __init__(self, name, data=None, indices=None):
        super(GamsSet, self).__init__(name,data,indices)


class GamsParameter(GamsDataElement,GamsArithmeticElement):
    """A parameter in GAMS"""
    def __init__(self, name, data=None, indices=None):
        super(GamsParameter, self).__init__(name,data,indices)



class GamsExpression(GamsArithmeticElement):
    """A GAMS expression tree"""
    def __init__(self,current,left=None,right=None):
        super(GamsExpression, self).__init__()
        self.current = current
        self.left = left
        self.right = right

    def __str__(self):
        if self.right is None and self.left is None:
            return str(self.current)
        else:
            main_expr = '{} {} {}'.format(self.left,self.current,self.right)
            return main_expr if not self.parenthesis else '({})'.format(main_expr)


class GamsFunctionTypeExpression(GamsExpression):
    """A function expresssion in Gams"""
    def __init__(self, funcname, args):
        super(GamsFunctionTypeExpression, self).__init__(self)
        self.funcname = funcname
        self.args = args

    def __str__(self):
        return '{}({})'.format(self.funcname,','.join(map(str,self.args)))


class GamsSum(GamsFunctionTypeExpression):
    """Gams summation function"""
    def __init__(self, over_set, arg):
        super(GamsSum, self).__init__('sum',(over_set.name,arg))

class GamsProd(GamsFunctionTypeExpression):
    """Gams product function"""
    def __init__(self, over_set, arg):
        super(GamsProd, self).__init__('prod',(over_set.name,arg))


if __name__ == '__main__':
    i = GamsSet('i')
    t = GamsSet('t')
    s = GamsSet('tt',indices=[i,t])
    x = GamsParameter('x',indices=[i,t])
    y = GamsParameter('y',indices=[i,t])
    sumofy = GamsProd(s,x+y)
    z = x+y+sumofy
    print 1/x+2*z/(y-x)*5+10.0
