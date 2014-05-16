import copy
import jinja2
import numpy as np
import gdx_utils as gdx

VALID_EQN_OPS = ["=e=","=l=","=g="]
VALID_V_TYPES = ['positive','binary','free']

def select_vtype(variables,vtype):
    return [var for var in variables if var.vtype==vtype]

def isnumber(val):
    try:
        float(val)
    except (ValueError,TypeError):
        return False
    return True

filters = {"select_vtype":select_vtype}

class GamspyAddSubExpression(object):
    """Gams elements that can be added or subtracted to create expressions"""
    def __init__(self, parenthesis=False):
        super(GamspyAddSubExpression, self).__init__()
        self.parenthesis = parenthesis

    def __add__(self,other):
        if not (isinstance(other,GamspyArithmeticExpression) or isnumber(other)):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamspyExpression('+',self,other)
    def __sub__(self,other):
        if isnumber(other):
            return GamspyExpression('-',self,other)
        if not isinstance(other,GamspyArithmeticExpression):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamspyExpression('-',self,other.parenthesized())
    def __radd__(self,other):
        return GamspyExpression(str(other))+self
    def __rsub__(self,other):
        return GamspyExpression(str(other))-self

    def parenthesized(self):
        new_element = copy.copy(self)
        new_element.parenthesis = True
        return new_element


class GamspyArithmeticExpression(GamspyAddSubExpression):
    """Gams elements that can be added, subtracted, multiplied and divided to create expressions."""
    def __init__(self,**kwargs):
        super(GamspyArithmeticExpression,self).__init__(**kwargs)

    def __div__(self,other):
        if isnumber(other):
            return GamspyExpression('/',self.parenthesized(),other)
        if not isinstance(other,GamspyArithmeticExpression):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamspyExpression('/',self.parenthesized(),other.parenthesized())
    def __mul__(self,other):
        if isnumber(other):
            return GamspyExpression('*',self.parenthesized(),other)
        if not isinstance(other,GamspyArithmeticExpression):
            raise ValueError('Arithmetic not allowed on instance of {}.'.format(other.__class__.__name__))
        return GamspyExpression('*',self.parenthesized(),other.parenthesized())
    def __rmul__(self,other):
        return GamspyExpression(str(other))*self
    def __rdiv__(self,other):
        return GamspyExpression(str(other))/self

    def __lt__(self,other):
        return GamspyEquationExpression('=l=',self,other)
    def __gt__(self,other):
        return GamspyEquationExpression('=g=',self,other)
    def __eq__(self,other):
        return GamspyEquationExpression('=e=',self,other)



class GamspyElement(object):
    """Gams elements such as a set or parameter"""
    def __init__(self, name, indices=None):
        super(GamspyElement, self).__init__()
        self.name = name
        self.indices = indices

    def __str__(self,show_indices=True):
        if show_indices and self.indices is not None:
            ind_list = []
            for ind in self.indices:
                try:
                    ind_list.append(str(ind.no_indices))
                except AttributeError:
                    ind_list.append(str(ind))
            return self.name + '({})'.format(','.join(ind_list))
        else:
            return self.name

    @property
    def no_indices(self):
        no_ind_elem = copy.copy(self)
        no_ind_elem.indices = None
        return no_ind_elem

    def with_indices(self,*indices):
        new_ind_elem = copy.copy(self)
        new_ind_elem.indices = indices
        return new_ind_elem

    def ix(self,*indices):
        if not indices:
            return self.no_indices
        else:
            return self.with_indices(*indices)


class GamspyAlias(GamspyElement,GamspyArithmeticExpression):
    """An alias in GAMS"""
    def __init__(self, name, aliasof):
        super(GamspyAlias, self).__init__(name=name)
        self.aliasof = aliasof

    def __getattr__(self,attr):
        return self.aliasof.__getattribute__(attr)

class GamspyVariable(GamspyElement,GamspyArithmeticExpression):
    """A variable in GAMS"""
    def __init__(self, name, indices=None, vtype="positive",up=None,lo=None,l=None,fx=None):
        super(GamspyVariable, self).__init__(name,indices)
        self.vtype = vtype.lower()
        if self.vtype not in VALID_V_TYPES:
            raise ValueError("Variable type {} is unknown.".format(self.vtype))
        self.up = up
        self.lo = lo
        self.l = l
        self.fx = fx

class GamspyDataElement(GamspyElement):
    """A Gams element that can contain data"""
    def __init__(self, name, data=None, indices=None):
        super(GamspyDataElement, self).__init__(name,indices)
        self.data = np.array(data)


class GamspySet(GamspyDataElement,GamspyAddSubExpression):
    """A set in GAMS"""
    def __init__(self, name, data=None, indices=None, aliasof=None):
        if indices is None:
            self.dim = 1
        else:
            self.dim = len(indices)
        if data is not None and self.dim==1:
            data = map(str,data)
        else:
            for i,row in enumerate(data):
                data[i] = map(str,row)
        super(GamspySet, self).__init__(name,data,indices)
        self.level = 0 if indices is None else 1 + max(i.level for i in self.indices)

    def add_to_db(self,db):
        if self.dim==1:
            gdx.set_from_1d_array(db,self.name,self.data)
        else:
            gdx.set_from_2d_array(db,self.name,self.data)

class GamspyParameter(GamspyDataElement,GamspyArithmeticExpression):
    """A parameter in GAMS"""
    def __init__(self, name, data=None, indices=None):
        super(GamspyParameter, self).__init__(name,data,indices)
        if self.data is not None:
            self.data = self.data.astype('float64')

    @property
    def ndim(self):
        return self.data.ndim - sum([1 if e==1 else 0 for e in self.data.shape])

    @property
    def data_2d(self):
        if self.data.ndim==1:
            return np.atleast_2d(self.data).T
        return np.atleast_2d(self.data)

    def add_to_db(self,db):
        if self.ndim == 1:
            gdx.param_from_1d_array(db,name=self.name, set_list=self.indices[0].data, values=self.data_2d)
        elif self.ndim == 2:
            gdx.param_from_2d_array(db,name=self.name, row_set=self.indices[0].data, col_set=self.indices[1].data, values=self.data_2d)
        else:
            raise ValueError('Cannot add data with more than 2 dimensions to GAMS db.')

    def create_from_series(self,series,idx_set):
        self.data = series.values.astype('float64')
        self.indices = [GamspySet(name=idx_set.name,data=series.index.values)]

    def create_from_dataframe(self,df,row_set,col_set):
        self.data = df.values.astype('float64')
        self.indices = [GamspySet(name=row_set.name,data=df.index.values),GamspySet(name=col_set.name,data=df.columns.values)]


class GamspyExpression(GamspyArithmeticExpression):
    """A GAMS expression tree"""
    def __init__(self,current,left=None,right=None):
        super(GamspyExpression, self).__init__()
        self.current = current
        self.left = left
        self.right = right

    def __str__(self):
        if self.right is None and self.left is None:
            return str(self.current)
        else:
            main_expr = '{} {} {}'.format(self.left,self.current,self.right)
            return main_expr if not self.parenthesis else '({})'.format(main_expr)


class GamspyFunctionTypeExpression(GamspyExpression):
    """A function expresssion in Gams"""
    def __init__(self, funcname, args):
        super(GamspyFunctionTypeExpression, self).__init__(self)
        self.funcname = funcname
        self.args = args

    def __str__(self):
        return '{}({})'.format(self.funcname,','.join(map(str,self.args)))

def func_over_sets(func,over_sets,arg,conditional=None):
    over_sets_arg = '({})'.format(','.join((s.name for s in over_sets)))
    if conditional is not None:
        over_sets_arg += '$({})'.format(conditional)
    return GamspyFunctionTypeExpression(func,(over_sets_arg,arg))
def gams_sum(*args,**kwargs):
    return func_over_sets('sum',*args,**kwargs)
def gams_prod(*args,**kwargs):
    return func_over_sets('prod',*args,**kwargs)

class GamspyEquationExpression(GamspyExpression):
    """An expression for an equation in Gams."""
    def __init__(self, current, left, right):
        super(GamspyEquationExpression, self).__init__(current, left, right)
        if current not in VALID_EQN_OPS:
            raise ValueError('{} is not a valid operator in an equation.'.format(current))



class GamspyEquation(GamspyElement):
    """A Gams 'equation', i.e. equality or inequality."""
    def __init__(self, name, expr, indices=None,conditional=None):
        super(GamspyEquation, self).__init__(name,indices)
        self.name = name
        self.indices = indices
        self.conditional = conditional
        self.expr = expr

    def __str__(self):
        return str(self.expr)


if __name__ == '__main__':
    i = GamspySet('i')
    t = GamspySet('t')
    s = GamspySet('tt',indices=[i])
    p1 = GamspyParameter('p1',indices=[i,t])
    p2 = GamspyParameter('p2',indices=[i,t])
    x = GamspyVariable('x',indices=[i,t])
    y = GamspyVariable('y',indices=[i,t])

    eq1 = GamspyEquation('eq1',(p1*x/(x+y) + p2*x*y < 2*x/p2),indices=[i,t])

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
