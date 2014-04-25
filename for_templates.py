import copy
import jinja2

VALID_EQN_OPS = ["=e=","=l=","=g="]

def isnumber(val):
    try:
        float(val)
    except (ValueError,TypeError):
        return False
    return True

class GamsArithmeticExpression(object):
    """Gams elements that can be added, subtracted, multiplied and divided to create expressions."""
    def __init__(self,parenthesis=False):
        super(GamsArithmeticExpression,self).__init__()
        self.parenthesis = parenthesis

    def __add__(self,other):
        if not (isinstance(other,GamsArithmeticExpression) or isnumber(other)):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('+',self,other)
    def __sub__(self,other):
        if isnumber(other):
            return GamsExpression('-',self,other)
        if not isinstance(other,GamsArithmeticExpression):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('-',self,other.parenthesized())
    def __div__(self,other):
        if isnumber(other):
            return GamsExpression('/',self.parenthesized(),other)
        if not isinstance(other,GamsArithmeticExpression):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamsExpression('/',self.parenthesized(),other.parenthesized())
    def __mul__(self,other):
        if isnumber(other):
            return GamsExpression('*',self.parenthesized(),other)
        if not isinstance(other,GamsArithmeticExpression):
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

    def __lt__(self,other):
        return GamsEquationExpression('=l=',self,other)

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


class GamsVariable(GamsElement,GamsArithmeticExpression):
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


class GamsParameter(GamsDataElement,GamsArithmeticExpression):
    """A parameter in GAMS"""
    def __init__(self, name, data=None, indices=None):
        super(GamsParameter, self).__init__(name,data,indices)



class GamsExpression(GamsArithmeticExpression):
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

def gams_sum(over_set,arg):
    return GamsFunctionTypeExpression('sum',(over_set.name,arg))
def gams_prod(over_set,arg):
    return GamsFunctionTypeExpression('prod',(over_set.name,arg))

class GamsEquationExpression(GamsExpression):
    """An expression for an equation in Gams."""
    def __init__(self, current, left, right):
        super(GamsEquationExpression, self).__init__(current, left, right)
        if current not in VALID_EQN_OPS:
            raise ValueError('{} is not a valid operator in an equation.'.format(current))



class GamsEquation(GamsElement):
    """A Gams 'equation', i.e. equality or inequality."""
    def __init__(self, name, expr, indices=None):
        super(GamsEquation, self).__init__(name,indices)
        self.name = name
        self.indices = indices
        self.expr = expr

    def __str__(self):
        return str(self.expr)


if __name__ == '__main__':
    i = GamsSet('i')
    t = GamsSet('t')
    s = GamsSet('tt',indices=[i])
    p1 = GamsParameter('p1',indices=[i,t])
    p2 = GamsParameter('p2',indices=[i,t])
    x = GamsVariable('x',indices=[i,t])
    y = GamsVariable('y',indices=[i,t])

    eq1 = GamsEquation('eq1',(p1*x/(x+y) + p2*x*y < 2*x/p2),indices=[i,t])

    context = {
        "title": "Test model",
        "sets": [i,t,s],
        "parameters": [p1,p2],
        "variables": [x,y],
        "equations": [eq1]
    }

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    template = env.get_template('base_gms.j2')

    print template.render(context)
