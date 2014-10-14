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
from gams import GamsWorkspace, GamsDatabase, GamsParameter, \
                 GamsSet, GamsVariable, GamsException
import re
from csv import writer

VALID_FIELDS = ["level","upper","lower","marginal"]

# Handle gdx files
class GdxReader(object):
    """Class to read GDX files"""
    def __init__(self,gdx_file):
        super(GdxReader, self).__init__()
        self.gdx_file = gdx_file

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, ex_type, ex_val, ex_trace):
        self.close()

    def open(self):
        self.ws = GamsWorkspace()
        self.db = self.ws.add_database_from_gdx(self.gdx_file)

    def close(self):
        del self.db, self.ws

    # Get a list of elements in a set named set_name
    def get_1d_set_elements(self,set_name):
        try:
            set_obj = self.db.get_set(set_name)
        except GamsException as e:
            raise GdxSymbolNotFoundError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(set_name,str(e)))
        if not isinstance(set_obj, GamsSet):
            raise TypeError("'{0}' is not a set in the current gdx.".format(set_name))
        return [rec.keys[0] for rec in set_obj]

    # Get elements of n-dimensional set as list of n-tuples
    def get_nd_set_elements(self,set_name):
        try:
            set_obj = self.db.get_set(set_name)
        except GamsException as e:
            raise GdxSymbolNotFoundError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(set_name,str(e)))
        if not isinstance(set_obj, GamsSet):
            raise TypeError("'{0}' is not a set in the current gdx.".format(set_name))
        return [tuple(rec.keys) for rec in set_obj]

    # Get value of parameter as dict indexed by tuples (key1,..,keyn)
    def get_parameter(self,param_name):
        try:
            param_obj = self.db.get_parameter(param_name)
        except GamsException as e:
            raise GdxSymbolNotFoundError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(param_name,str(e)))
        try:
            if not param_obj.first_record().keys:
                return param_obj.first_record().value
        except GamsException as e:
            raise GdxSymbolEmptyError("Symbol {} appears to be empty.".format(param_name))
        return dict((tuple(rec.keys),rec.value) for rec in param_obj)

    # Get property of equation or variable as dict indexed by tuples (key_1,..,key_n)
    def get_eq_or_var(self,name,obj_type,field):
        # Get correct symbol
        try:
            if obj_type in ["variable","equation"]:
                obj = self.db.get_symbol(name)
            else:
                raise ValueError("Object type is not recognised.")
        except GamsException as e:
            raise GdxSymbolNotFoundError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(name,str(e)))
        # Get correct field
        if field in VALID_FIELDS:
            return dict((tuple(rec.keys),getattr(rec,field)) for rec in obj)
        else:
            raise ValueError("Field type is not recognised.")

    # Quick access functions
    def get_eq_level(self,name):
        return self.get_eq_or_var(name,obj_type="equation",field="level")
    def get_var_level(self,name):
        return self.get_eq_or_var(name,obj_type="variable",field="level")
    def get_eq_marginal(self,name):
        return self.get_eq_or_var(name,obj_type="equation",field="marginal")
    def get_var_marginal(self,name):
        return self.get_eq_or_var(name,obj_type="variable",field="marginal")
    def get_eq_upper(self,name):
        return self.get_eq_or_var(name,obj_type="equation",field="upper")
    def get_var_upper(self,name):
        return self.get_eq_or_var(name,obj_type="variable",field="upper")
    def get_eq_lower(self,name):
        return self.get_eq_or_var(name,obj_type="equation",field="lower")
    def get_var_lower(self,name):
        return self.get_eq_or_var(name,obj_type="variable",field="lower")

    # Read symbols and place names in list depending on type
    def get_symbol_names(self):
        self.param_names = []
        self.set_names = []
        self.var_names = []
        self.eq_names = []
        for s in GamsIter(self.db):
            if isinstance(s, GamsParameter):
                self.param_names.append(s.name)
            elif isinstance(s, GamsSet):
                self.set_names.append(s.name)
            elif isinstance(s, GamsVariable):
                self.var_names.append(s.name)
            elif isinstance(s, GamsEquation):
                self.eq_names.append(s.name)
            else:
                raise Exception("Symbol type of '{0}' is not recognised.".format(s.name))

    # Return sets matching a regex pattern
    def find_sets_regex(self,pattern):
        return [s for s in self.set_names if re.match(pattern,s)]

# Wrap GamsDatabase iterator to handle exception in next
class GamsIter(object):
    """Iterator for Gams db"""
    def __init__(self, db):
        super(GamsIter, self).__init__()
        self.db_iter = db.__iter__()

    def __iter__(self):
        return self

    # Return next but skip if 'unknown symbol type'
    def next(self):
        while True:
            try:
              return self.db_iter.next()
            except StopIteration:
              raise
            except GamsException as e:
                print str(e)
                if 'unkown symbol type' in str(e):
                    continue
                else:
                    raise

class GdxSymbolNotFoundError(Exception):
    pass

class GdxSymbolEmptyError(Exception):
    pass