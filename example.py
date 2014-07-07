from model import GamspyModel
from gdx import GdxReader
import gdx_utils
from types import *
import numpy as np

# This file must be run with "python -m gamspy.example" from directory level above

f_cost = 90.0

i = GamspySet('i',data=['seattle','san-diego'])
j = GamspySet('j',data=['new-york', 'chicago', 'topeka'])

a = GamspyParameter('a',indices=[i],data=[350,600])
b = GamspyParameter('b',indices=[j],data=[325,300,275])
d_matrix = np.array([[2.5,1.7,1.8],[2.5,1.8,1.4]])
c_matrix = f_cost * d_matrix / 1000.0
c = GamspyParameter('c',indices=[i,j],data=c_matrix)
d = GamspyParameter('d',indices=[i,j],data=d_matrix)

x = GamspyVariable('x',indices=[i,j]) # default variable type is positive
z = GamspyVariable('z',vtype='free')

# Equations objects are created with name, expression and indices (if applicable)
cost = GamspyEquation('cost', z == gams_sum([i,j], c*x))
supply = GamspyEquation('supply', gams_sum([j],x) < a, indices=[i])
demand = GamspyEquation('demand', gams_sum([i],x) > b, indices=[j])

m = GamspyModel(name='transport',model_file='D:/git/gamspy/tmp/transport.gms',data_file='D:/git/gamspy/tmp/transport_in.gdx',out_file='D:/git/gamspy/tmp/transport_out.gdx',gams_exec='C:/GAMS/win64/23.8/gams.exe')
m.sets = {'i':i, 'j':j}
m.parameters = {'a':a, 'b':b, 'c':c, 'd':d}
m.variables = {'x':x, 'z':z}
m.equations = {'cost':cost, 'supply':supply, 'demand':demand}
m.obj_var = m.variables['z']

m.write_data_file()
m.write_model_file()
t = m.create_thread()
t.start()
t.join()

r = GdxReader(m.out_file)
# Objects from GDX are returned as tuple-indexed dict
x_from_gdx = r.get_var_level('x')
# They can be parsed to a numpy array using gdx_utils
x_l = gdx_utils.parse_along_2d(x_from_gdx,list(i.data),list(j.data))
for (row,col),val in np.ndenumerate(x_l):
    print "From {} to {}: {} cases".format(i.data[row],j.data[col],val)
# In the case of the scalar z we just read the first value
z = r.get_var_level('z').values()[0]

print "Total cost is {} kUSD".format(z)



# NOTE: A model can also be constructed by inheriting from GamspyModel
# class TransportModel(GamspyModel):
#     """Transportation example model"""
#     def __init__(self,**kwargs):
#         super(TransportModel, self).__init__(**kwargs)

#         # Sets and parameters are properties of super-class
#         self.sets = {
#             'i': GamspySet('i',data=['seattle','san-diego']),
#             'j': GamspySet('j',data=['new-york', 'chicago', 'topeka'])
#         }
#         self.parameters = {
#             'a': GamspyParameter('a',indices=[self.sets['i']],data=[350,600]),
#             'b': GamspyParameter('b',indices=[self.sets['j']],data=[325,300,275])
#         }
#         ...