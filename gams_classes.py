import os
import subprocess as sp
from PySide import QtCore

class GamsModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, gams_dir, model_file, res_file):
        super(GamsModel, self).__init__()
        self.gams_dir = os.path.abspath(gams_dir)
        os.chdir(self.gams_dir)
        self.model_file = model_file
        self.res_file = res_file

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

    #gams_finished = QtCore.Signal()

    # Constructor
    def __init__(self,model):
        super(GamsThread, self).__init__()
        self.model = model

    # Run thread
    def run(self):
        os.chdir(self.model.gams_dir)
        sp.call(["gams", self.model.model_file])
        self.read_results()
    #   self.gams_finished.emit()

    # Returns results dictionary
    def get_results(self):
        return self._results

    # Read results from the put file generated from GAMS
    # Place in a dictionary {(set_key1,...): value}
    def read_results_as_tuple_dict(self):
        self._results = {}
        with open(self.model.res_file,'r') as f:
            for line in f:
                parts = line.split()
                self._results[tuple(parts[:-1])] = float(parts[-1])

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


class GamsElement(object):
    """Class to handle an element such as a set or parameter"""
    def __init__(self, name, data):
        super(GamsElement, self).__init__()
        self.name = name
        self.data = data
        self.data_start = '/'
        self.data_end = '/;'

    def write_to_inc(self,inc_file,include_head_foot=True):
        with open(inc_file,'wb') as f:
            # Write header
            if include_head_foot:
                f.write('{name}{keys} {data_start}\n'
                            .format(name=self.name,
                                    keys=self._get_keys_as_string(),
                                    data_start=self.data_start))
            # Write data
            f.write('{data}\n'.format(data='\n'.join(self._get_data_as_strings())))
            # Write footer
            if include_head_foot:
                f.write('{data_end}'.format(data_end=self.data_end))

    def _get_keys_as_string(self):
        raise NotImplementedError("Abstract class. Use subclasses!")

    def _get_data_as_strings(self):
        raise NotImplementedError("Abstract class. Use subclasses!")

    def data():
        doc = "The data property."
        def fget(self):
            return self._data
        def fset(self, value):
            self._data = value
        def fdel(self):
            del self._data
        return locals()
    data = property(**data())

class GamsSet(GamsElement):
    """Class to represent a set in GAMS"""
    def __init__(self, name, elements):
        super(GamsSet, self).__init__(name,elements)

    def _get_keys_as_string(self):
        return ''

    def _get_data_as_strings(self):
        return self.data

class GamsParameter(GamsElement):
    """Class to represent a parameter in GAMS"""
    def __init__(self, name, data, set_names=[]):
        super(GamsParameter, self).__init__(name,data)
        self.set_names = set_names

    def _get_keys_as_string(self):
        return '' if not self.set_names else '('+','.join(self.set_names)+')'

    def _get_data_as_strings(self):
        return ['.'.join(key)+'\t\t'+str(val) for key,val in self.data.items()]





