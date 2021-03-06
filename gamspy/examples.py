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
# above. You can also run the example by importing the transport example and
# running it from somewhere else:
#
#    from gamspy.examples import TransportModel
#    from gamspy.utils import make_tmp_dir
#
#    with make_tmp_dir() as d:
#        ex = TransportModel(d)
#        ex.run()
#        ex.print_results()
#
# or through the shortcut:
#
#    import gamspy.examples as ex
#    ex.run()
#
# Some settings in this file must be adapted to fit your setup.
from gamspy.model import GamspyModel
import gamspy.gdx as gdx
import gamspy.gdx_utils
from gamspy.types import *
from gamspy.utils import make_tmp_dir
import numpy as np

class TransportModel(object):
    """Transport example problem."""
    def __init__(self,
                    work_dir,
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
        test = GamspyParameter('test')

        x = GamspyVariable('x',indices=[i,j]) # default variable type is positive
        z = GamspyVariable('z',vtype='free')

        # Equations objects are created with name, expression and indices (if
        # applicable)
        cost = GamspyEquation('cost', z == gams_sum([i,j], c*x))
        supply = GamspyEquation('supply', gams_sum([j],x) < a, indices=[i])
        demand = GamspyEquation('demand', gams_sum([i],x) > b, indices=[j])

        # Creation of model object
        # Either make sure gams.exe is on your PATH or add a gams_exec argument
        # to the object constructor, specifying where to find the correct
        # gams.exe
        self.m = GamspyModel(
                    name='transport',
                    work_dir=work_dir)

        # Add sets, parameters, variables, and equations to model. Dictionary
        # keys does not have to be identical to element names. Keys are used
        # to retrieve element objects from model.
        self.m.sets = {'i':i, 'j':j}
        self.m.parameters = {'a':a, 'b':b, 'c':c, 'd':d, 'test': test}
        self.m.variables = {'x':x, 'z':z}
        self.m.equations = {'cost':cost, 'supply':supply, 'demand':demand}
        self.m.obj_var = self.m.variables['z']

    def run(self):
        # Write files and run GAMS
        self.m.write_data_file()
        self.m.write_model_file()
        self.m.run_model()

    def get_shipping_flows(self):
        # Read results by using GdxReader in a 'with'-statement
        with gdx.get_reader(self.m.out_file) as r:
            # Objects from GDX are returned as tuple-indexed dict
            x_from_gdx = r.get_var_level('x')

        # They can be parsed to a numpy array using gdx_utils
        i = self.m.sets['i']
        j = self.m.sets['j']
        x_l = gdx_utils.parse_along_2d(x_from_gdx,list(i.data),list(j.data))
        return {(i.data[row],j.data[col]): val for
                    (row,col),val in np.ndenumerate(x_l)}

    def get_tot_cost(self):
        with gdx.get_reader(self.m.out_file) as r:
            # In the case of the scalar z we just read the first value
            return r.get_var_level('z').values()[0]

    def print_results(self):
        # Loop through result rows and print
        for (from_loc,to_loc),val in self.get_shipping_flows().items():
            print "From {} to {}, ship {:.0f} cases" \
                        .format(from_loc,to_loc,val)

        print "Total cost is {} kUSD".format(self.get_tot_cost())

def run():
    with make_tmp_dir() as d:
        ex = TransportModel(d)
        ex.run()
        ex.print_results()

if __name__ == '__main__':
    # The example model can be run through:
    with make_tmp_dir() as d:
        ex = TransportModel(d)
        ex.run()
        ex.print_results()




# NOTE: A model can also be constructed by inheriting from GamspyModel
# class TransportModel(GamspyModel):
#     """Transportation example model"""
#     def __init__(self,**kwargs):
#         super(TransportModel, self).__init__(**kwargs)
#
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