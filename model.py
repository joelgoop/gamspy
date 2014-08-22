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
import os
import operator
import jinja2
import gams
import re
import gdx_utils as gdx
from .types import *
import utils

class GamspyModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, name,work_dir,
                    model_file=None,
                    data_file=None,
                    out_file=None,
                    status_file=None,
                    title=None,
                    author=None,
                    options = None,
                    opt_settings=None,
                    gams_exec=None):
        super(GamspyModel, self).__init__()
        self.gams_exec = gams_exec
        if not os.path.isdir(work_dir):
            raise ValueError("The given work dir '{}' is not a directory.".format(work_dir))
        self.work_dir = work_dir


        self.title = title
        self.name = name
        self.author = author

        self.model_file = self._work_file(model_file,"{}_model.gms".format(self.name))
        self.data_file = self._work_file(data_file,"{}_input.gdx".format(self.name))
        self.out_file = self._work_file(out_file,"{}_output.gdx".format(self.name))
        self.status_file = self._work_file(status_file,"{}_statuses.txt".format(self.name))

        self.accept_codes = {"solvestat": [1], "modelstat": [1,8]}

        self.options = {"optcr": 1e-5, "tolinfeas": 1e-10}
        if options:
            self.options.update(options)
        self.opt_settings = {}
        if opt_settings:
            self.opt_settings.update(opt_settings)

        self.maximize = False
        self.model_type = "lp"
        self.solver = "cplex"

        self.opt_file = os.path.join(self.work_dir,self.solver+".opt")
        self.template_dirs = [os.path.join(os.path.dirname(__file__), 'templates')]

        self.sets = {}
        self.aliases = {}
        self.parameters = {}
        self.variables = {}
        self.equations = {}

        self.output_parameters = []
        self.presolve_assign = []
        self.dump = True

        self.header_string = """*-----------------------------------------------------------------------------
* This file has been automatically rendered by gamspy
*-----------------------------------------------------------------------------
"""

    def run_model(self):
        self.statuses = {}

        utils.run_gams(model_file=self.model_file,work_dir=self.work_dir,gams_exec=self.gams_exec)

        # Read status codes from returns file
        with open(self.status_file,'r') as f:
            for line in f:
                key,status = line.split(',')
                m = re.match('(\d+)\s([\w ]+)',status)
                self.statuses[key] = (int(float(m.group(1))),m.group(2))

        # Raise exception if status codes are not acceptable
        status_str = ""
        for key,(code,status) in self.statuses.items():
            if code not in self.accept_codes[key]:
                raise Exception("There was an unacceptable status code from GAMS. {} is {}: '{}'.".format(key,code,status))
            status_str += "{} is {}: '{}'. ".format(key,code,status)
        print "{}\nGAMS finished without errors.".format(status_str)

    def write_data_file(self):
        ws = gams.GamsWorkspace()
        db = ws.add_database()
        for s in sorted(self.sets.values(), key=operator.attrgetter('level')):
            print "Adding set: {}".format(s.name)
            try:
                s.add_to_db(db)
            except Exception:
                print s
                raise
        for p in self.parameters.values():
            print "Adding parameter: {}".format(p.name)
            try:
                p.add_to_db(db)
            except Exception:
                print p
                raise
        db.export(self.data_file)

    def write_model_file(self,template='base_gms.j2',optfile_template='base_optfile.j2'):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dirs))
        env.filters.update(utils.j2env['filters'])
        env.tests.update(utils.j2env['tests'])
        env.globals.update(utils.j2env['globals'])

        template = env.get_template(template)
        opt_template = env.get_template(optfile_template)

        with open(self.model_file,'w') as f:
            f.write(self.header_string+template.render(self.__dict__))
        with open(self.opt_file,'w') as f:
            f.write(self.header_string+opt_template.render({"settings":self.opt_settings}))

    def _work_file(self,filename,default):
        if not filename:
            return os.path.join(self.work_dir,default)
        else:
            return os.path.join(self.work_dir,filename)


