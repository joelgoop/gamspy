# gamspy - Build and run GAMS models from Python
# Copyright (C) 2014 Joel Goop
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# USAGE
#
# This file can be run with "python -m gamspy.examples" from directory level
# above. You can also by importing the transport example and running it from
# somewhere else:
#
#   from gamspy.examples import TransportModel
#
#   ex = TransportModel()
#   ex.run()
#   ex.print_results()
#
# Some settings in this file must be adapted to fit your setup.
from model import GamspyModel
from gdx import GdxReader
import gdx_utils
from .types import *
import numpy as np

class TransportModel(object):
    """Transport example problem."""
    def __init__(self,
                    f_cost=90.0,
                    a_in=[350,600],
                    b_in=[325,300,275],
                    d_in=[[2.5,1.7,1.8],[2.5,1.8,1.4]]
                ):
        i = GamspySet('i',data=['seattle','san-diego'])
        j = GamspySet('j',data=['new-york', 'chicago', 'topeka'])

        a = GamspyParameter('a',indices=[i],data=a_in)
        b = GamspyParameter('b',indices=[j],data=b_in)
        d_matrix = np.array(d_in)
        c_matrix = f_cost * d_matrix / 1000.0
        c = GamspyParameter('c',indices=[i,j],data=c_matrix)
        d = GamspyParameter('d',indices=[i,j],data=d_matrix)

        x = GamspyVariable('x',indices=[i,j]) # default variable type is positive
        z = GamspyVariable('z',vtype='free')

        # Equations objects are created with name, expression and indices (if
        # applicable)
        cost = GamspyEquation('cost', z == gams_sum([i,j], c*x))
        supply = GamspyEquation('supply', gams_sum([j],x) < a, indices=[i])
        demand = GamspyEquation('demand', gams_sum([i],x) > b, indices=[j])

        # Creation of model object - MODIFY ARGUMENTS TO FIT YOUR SETUP
        self.m = GamspyModel(
                    name='transport',
                    model_file='D:/git/gamspy/tmp/transport.gms',
                    data_file='D:/git/gamspy/tmp/transport_in.gdx',
                    out_file='D:/git/gamspy/tmp/transport_out.gdx',
                    gams_exec='C:/GAMS/win64/23.8/gams.exe')
        # Add sets, parameters, variables, and equations to model Dictionary
        # keys does not have to be identical to element names. Keys are used
        # to retrieve element objects from model.
        self.m.sets = {'i':i, 'j':j}
        self.m.parameters = {'a':a, 'b':b, 'c':c, 'd':d}
        self.m.variables = {'x':x, 'z':z}
        self.m.equations = {'cost':cost, 'supply':supply, 'demand':demand}
        self.m.obj_var = self.m.variables['z']

    def run(self):
        # Write files and run GAMS
        self.m.write_data_file()
        self.m.write_model_file()
        t = self.m.create_thread()
        t.start()
        t.join()

    def print_results(self):
        # Read results
        r = GdxReader(self.m.out_file)
        # Objects from GDX are returned as tuple-indexed dict
        x_from_gdx = r.get_var_level('x')
        # They can be parsed to a numpy array using gdx_utils
        i = self.m.sets['i']
        j = self.m.sets['j']
        x_l = gdx_utils.parse_along_2d(x_from_gdx,list(i.data),list(j.data))
        for (row,col),val in np.ndenumerate(x_l):
            print "From {} to {}, ship {:.0f} cases".format(i.data[row],j.data[col],val)
        # In the case of the scalar z we just read the first value
        z = r.get_var_level('z').values()[0]
        print "Total cost is {} kUSD".format(z)

if __name__ == '__main__':
    # The example model can be run through:
    ex = TransportModel()
    ex.run()
    ex.print_results()




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
#             'a': GamspyParameter('a',
#                               indices=[self.sets['i']],data=[350,600]),
#             'b': GamspyParameter('b',
#                               indices=[self.sets['j']],data=[325,300,275])
#         }
#         ...