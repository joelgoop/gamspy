from gams import *
import re
from ..sqlite_db.db_classes import *
from csv import writer

# Handle gdx files
class GdxReader(object):
    """Class to read GDX files"""
    def __init__(self,gdx_file):
        super(GdxReader, self).__init__()
        self.gdx_file = gdx_file
        self.ws = GamsWorkspace()
        self.db = self.ws.add_database_from_gdx(self.gdx_file)
        self.get_symbol_names()

    # Get a list of elements in a set named set_name
    def get_1d_set_elements(self,set_name):
        try:
            set_obj = self.db.get_set(set_name)
        except GamsException as e:
            raise ValueError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(set_name,str(e)))
        if not isinstance(set_obj, GamsSet):
            raise TypeError("'{0}' is not a set in the current gdx.".format(set_name))
        return [rec.keys[0] for rec in set_obj]

    # Get elements of n-dimensional set as list of n-tuples
    def get_nd_set_elements(self,set_name):
        try:
            set_obj = self.db.get_set(set_name)
        except GamsException as e:
            raise ValueError("A symbol named '{0}' could not be retrieved.\nOrig. msg: {1}".format(set_name,str(e)))
        if not isinstance(set_obj, GamsSet):
            raise TypeError("'{0}' is not a set in the current gdx.".format(set_name))
        return [tuple(rec.keys) for rec in set_obj]

    # Get value of parameter as dict indexed by tuples (key1,..,keyn)
    def get_parameter(self,param_name):
        param_obj = self.db.get_parameter(param_name)
        return dict((tuple(rec.keys),rec.value) for rec in param_obj)

    # Get property of equation or variable as dict indexed by tuples (key_1,..,key_n)
    def get_eq_or_var(self,name,obj_type,field):
        # Get correct symbol
        if obj_type=="variable":
            obj = self.db.get_variable(name)
        elif obj_type=="equation":
            obj = self.db.get_equation(name)
        else:
            raise ValueError("Object type is not recognised.")
        # Get correct field
        if field=="level":
            return dict((tuple(rec.keys),rec.level) for rec in obj)
        elif field=="upper":
            return dict((tuple(rec.keys),rec.upper) for rec in obj)
        elif field=="lower":
            return dict((tuple(rec.keys),rec.lower) for rec in obj)
        elif field=="marginal":
            return dict((tuple(rec.keys),rec.marginal) for rec in obj)
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

    # Insert parameter values into new table in sqlite database
    def get_parameter_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["value"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT"],include_id=False)
        param_obj = self.db.get_parameter(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.value,) for rec in param_obj))

    # Insert variable upper and level values to sqlite db
    def get_var_level_upper_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["level","upper"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT","SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_variable(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.level,rec.upper) for rec in var_obj))

    # Insert variable level values to sqlite db
    def get_var_level_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["level"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_variable(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.level,) for rec in var_obj if rec.level > 0))

    # Insert variable marginal values to sqlite db
    def get_var_marginal_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["level"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_variable(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.level,) for rec in var_obj if rec.marginal > 0))

    # Insert variable level and marginal values to sqlite db
    def get_var_level_marginal_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["level","marginal"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT","SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_variable(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.level,rec.marginal) for rec in var_obj))

    # Insert variable level, upper and marginal values to sqlite db
    def get_var_all_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["level","upper","marginal"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT","SMALLFLOAT","SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_variable(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.level,rec.upper,rec.marginal) for rec in var_obj))

    # Insert equation marginal values to sqlite db
    def get_eq_marginal_to_sqlite(self,name,keys,types,db_obj):
        cols = keys+["marginal"]
        db_obj.create_table(name,cols,types+["SMALLFLOAT"],include_id=False)
        var_obj = self.db.get_equation(name)
        db_obj.insert_data(name,cols,(tuple(rec.keys)+(rec.marginal,) for rec in var_obj if rec.marginal > 0))

    # Write variable upper and level values to a csv file
    def get_var_level_upper_to_csv(self,name,keys,csv_file):
        w = writer(open(csv_file,'wb'),dialect='excel')
        cols = keys + ["level","upper"]
        var_obj = self.db.get_variable(name)
        w.writerows((tuple(rec.keys)+(rec.level,rec.upper) for rec in var_obj))

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


if __name__ == '__main__':
    #gdx_file = "D:\\data\\gdxtest\\Exchange_ELIN_EPOD_ClimateMarket121207.gdx"
    #gdx_file = "D:\\data\\gdxtest\\regional_EPOD.gdx"
    gdx_file = "D:\\data\\gdxtest\\regional_EPOD.gdx"
    db_file = "D:\\data\\gdxtest\\test.db"
    db_obj = DataBase(db_file)
    gdx_r = GdxReader(gdx_file)
    gdx_r.get_parameter_to_sqlite("elec_production",["p_no","t","reg"],["INT","INT","TEXT"],db_obj)