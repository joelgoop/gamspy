import os
import subprocess as sp
from PySide import QtCore

class GamsModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, gams_dir, model_file, res_file=None):
        super(GamsModel, self).__init__()
        self.gams_dir = os.path.abspath(gams_dir)
        os.chdir(self.gams_dir)
        self.model_file = model_file
        self.res_file = res_file

    # Returns results dictionary
    def get_results(self):
        return self._results

    # Read results from the put file generated from GAMS
    # Place in a dictionary {(set_key1,...): value}
    def read_results_as_tuple_dict(self):
        self._results = self.import_results(self.res_file)

    @staticmethod
    def import_results(res_file):
        with open(res_file,'r') as f:
            return {tuple(parts[:-1]): float(parts[-1]) for parts in (line.split() for line in f)}

    def full_file_name(self,f_name):
        return self.gams_dir + '/' + f_name

    # Property containing the model file name
    def model_file():
        doc = "The model_file property."
        def fget(self):
            return self._model_file
        def fset(self, value):
            if os.path.isfile(self.gams_dir+'/'+value):
                if 'gms'==os.path.splitext(value)[1][1:]:
                    self._model_file = value
                else:
                    raise Exception('Model file type is not .gms.\n'+value)
            else:
                raise Exception('Model file does not exist.\n'+value)
        def fdel(self):
            del self._model_file
        return locals()
    model_file = property(**model_file())

    # Property containing the result file name
    def res_file():
        doc = "The res_file property."
        def fget(self):
            return self._res_file
        def fset(self, value):
            self._res_file = value
        def fdel(self):
            del self._res_file
        return locals()
    res_file = property(**res_file())



class GamsThread(QtCore.QThread):
    """Class to run GAMS in a separate QThread"""

    # Constructor
    def __init__(self,model,gams_exec='C:/GAMS/win64/23.9/gams.exe'):
        super(GamsThread, self).__init__()
        self.model = model
        self.gams_exec = gams_exec
        allowed_gams_files = ["C:/GAMS/win64/23.8/gams.exe","C:/GAMS/win64/23.9/gams.exe","C:/GAMS/win64/24.0/gams.exe","C:/GAMS/win64/24.1/gams.exe"]
        if self.gams_exec not in allowed_gams_files:
            raise ValueError("Input for GAMS executable is not allowed.")

    # Run thread
    def run(self):
        p = sp.Popen([self.gams_exec,self.model.model_file],cwd=self.model.gams_dir)
        p.wait()
        if p.returncode != 0:
            raise Exception("GAMS returned with an error. Return code is {}.".format(p.returncode))
        if self.model.res_file != None:
            self.read_results()

    # Returns results dictionary
    def get_results(self):
        return self._results

    # Read results from the put file generated from GAMS
    # Place in a dictionary {(set_key1,...): value}
    def read_results_as_tuple_dict(self):
        with open(self.model.res_file,'r') as f:
            self._results = {tuple(parts[:-1]): float(parts[-1]) for parts in (line.split() for line in f)}

    # Read results from the put file generated from GAMS
    def read_results(self):
        f = open(self.model.res_file,'r')
        self._results = dict()
        for line in f:
            parts = line.split()
            self._results = self.make_dict(parts,self._results)
        f.close()

    # Make dictionary of results
    def make_dict(self,current_list,level_above):
        if len(current_list)==2:
            level_above[current_list[0]] = float(current_list[1])
            return level_above
        else:
            if not level_above.has_key(current_list[0]):
                level_above[current_list[0]]=dict()
            level_above[current_list[0]] = self.make_dict(current_list[1:],level_above[current_list[0]])
            return level_above