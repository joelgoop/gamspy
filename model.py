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
import subprocess as sp
import threading
import jinja2
import gams
import gdx_utils as gdx
from .types import *

class GamspyModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, model_file,
                    data_file,
                    out_file,
                    title=None,
                    name=None,
                    options = None,
                    gams_exec='C:/GAMS/win64/23.8/gams.exe'):
        super(GamspyModel, self).__init__()
        if not os.path.isfile(gams_exec):
            raise ValueError("File {} is not a file.".format(gams_exec))
        self.gams_exec = gams_exec
        self.data_file = data_file
        self.out_file = out_file
        self.model_dir,self.model_file = os.path.split(os.path.abspath(model_file))
        self.title = title
        self.name = name

        self.options = {"optcr": 1e-4, "nodlim": 150000, "reslim": 100000, "iterlim": 4000000}
        if options:
            self.options.update(options)

        self.maximize = False
        self.model_type = "lp"

        self.template_dirs = [os.path.join(os.path.dirname(__file__), 'templates')]

        self.sets = {}
        self.aliases = {}
        self.parameters = {}
        self.variables = {}
        self.equations = {}


    def create_thread(self):
        return threading.Thread(target=self.run_model)

    def run_model(self):
        print "Running GAMS on {} in {}".format(self.model_file,self.model_dir)
        p = sp.Popen([self.gams_exec,self.model_file],cwd=self.model_dir)
        p.wait()
        if p.returncode != 0:
            raise Exception("GAMS returned with an error. Return code is {}.".format(p.returncode))
        print "GAMS finished without errors."

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

    def write_model_file(self,template='base_gms.j2'):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dirs))
        env.filters.update(filters)
        template = env.get_template(template)

        with open(os.path.join(self.model_dir,self.model_file),'w') as f:
            f.write(template.render(self.__dict__))