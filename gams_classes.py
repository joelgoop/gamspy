import os
import subprocess as sp
from PySide import QtCore
from ..misc.helper_classes import Struct

class GamsModel(object):
    """Class that contains necessary data to run a GAMS model"""
    def __init__(self, gams_dir, model_file, res_file=None, elem_collections=None):
        super(GamsModel, self).__init__()
        self.gams_dir = os.path.abspath(gams_dir)
        os.chdir(self.gams_dir)
        self.model_file = model_file
        self.res_file = res_file
        self.elem_collections = elem_collections if elem_collections else []

    def add_element_collection(self,elem_collection):
        self.elem_collections.append(elem_collection)

    # Write all elements to their respective files
    def write_elements(self):
        for c in self.elem_collections:
            c.write_elements()

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


class GamsElement(object):
    """Class to handle an element such as a set or parameter"""
    def __init__(self, name, data, identifier):
        super(GamsElement, self).__init__()
        self.name = name
        self.data = data
        self.identifier = identifier
        self.data_start = '/'
        self.data_end = '/;\n'

    def write_to_inc(self,f,include_head_foot=True):
        # Write header
        if include_head_foot:
            f.write('{identifier} {name}{keys} {data_start}\n'
                        .format(identifier=self.identifier,
                                name=self.name,
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
        super(GamsSet, self).__init__(name,elements,'SET')

    def _get_keys_as_string(self):
        return ''

    def _get_data_as_strings(self):
        return self.data


class GamsParameter(GamsElement):
    """Class to represent a parameter in GAMS"""
    def __init__(self, name, data, set_names=None):
        super(GamsParameter, self).__init__(name,data,'PARAMETER')
        self.set_names = set_names if set_names else []
        if not set_names:
            self._get_data_as_strings = self._get_data_as_strings_1d
        else:
            self._get_data_as_strings = self._get_data_as_strings_nd

    def _get_keys_as_string(self):
        return '' if not self.set_names else '('+','.join(self.set_names)+')'

    def _get_data_as_strings_nd(self):
        return ['.'.join(key)+'\t\t'+str(val) for key,val in self.data]

    def _get_data_as_strings_1d(self):
        return [str(self.data)]


class GamsElementCollection(object):
    """Handle collections of elements"""
    def __init__(self, elem_file, elems=None):
        super(GamsElementCollection, self).__init__()
        self.elems = elems if elems else []
        self.elem_file = elem_file

    def add_element(self,element):
        self.elems.append(element)

    # Write all elements to file
    def write_elements(self):
        with open(self.elem_file,'wb') as f:
            for el in self.elems:
                el.write_to_inc(f)

class GamsGlobal(GamsElement):
    """Class to represent a global variable in GAMS"""
    def __init__(self, name, value):
        super(GamsGlobal, self).__init__(name,value,identifier='$setglobal')

    def write_to_inc(self,f):
        f.write('{identifier} {name} {value}\n'.format(identifier=self.identifier,name=self.name,value=self.data))

