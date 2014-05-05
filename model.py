import os
import subprocess as sp
import threading
import jinja2
import gams
import gdx_utils as gdx
from .types import *



class GamspyModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, title=None,
                    model_file='D:/data/wedd_v2/wedd2_test.gms',
                    data_file='D:/data/wedd_v2/data.gdx',
                    out_file='D:/data/wedd_v2/results.gdx',
                    gams_exec='C:/GAMS/win64/23.9/gams.exe'):
        super(GamspyModel, self).__init__()
        if not os.path.isfile(gams_exec):
            raise ValueError("File {} is not a file.".format(gams_exec))
        self.gams_exec = gams_exec
        self.data_file = data_file
        self.out_file = out_file
        self.model_dir,self.model_file = os.path.split(os.path.abspath(model_file))
        self.title = title

        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')

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
        for s in self.sets.values():
            print "Adding set: {}".format(s.name)
            s.add_to_db(db)
        for p in self.parameters.values():
            print "Adding parameter: {}".format(p.name)
            p.add_to_db(db)
        db.export(self.data_file)

    def write_model_file(self):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir))
        env.filters.update(filters)
        template = env.get_template('base_gms.j2')

        context = {
            "title": self.title,
            "sets": self.sets,
            "parameters": self.parameters,
            "variables": self.variables,
            "equations": self.equations,
            "gdx_in": self.data_file,
            "gdx_out": self.out_file
        }

        with open(os.path.join(self.model_dir,self.model_file),'w') as f:
            f.write(template.render(context))


if __name__ == '__main__':
    m = GamspyModel(gams_exec='C:/GAMS/win64/23.8/gams.exe')
    i = GamspySet('i',data=['test','test2','test3'])
    t = GamspySet('t')
    s = GamspySet('tt',indices=[i])
    p1 = GamspyParameter('p1',indices=[i,t])
    p2 = GamspyParameter('p2',indices=[i,t])
    x = GamspyVariable('x',indices=[i,t])
    y = GamspyVariable('y',indices=[i,t])

    eq1 = GamspyEquation('eq1',(p1*x/(x+y) + p2*x*y < 2*x/p2),indices=[i,t])

    m.sets = [i,t,s]
    m.parameters = [p1,p2]
    m.variables = [x,y]
    m.equations = [eq1]
    print "Generating file."
    m.write_model_file('test.gms')