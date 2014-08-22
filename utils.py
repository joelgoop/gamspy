import tempfile
import shutil
import contextlib
import subprocess as sp
import os


@contextlib.contextmanager
def make_tmp_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir)

def isnumber(val):
    try:
        float(val)
    except (ValueError,TypeError):
        return False
    return True

def select_vtype(variables,vtype):
    return [var for var in variables if var.vtype==vtype]

# Add equalto test from new jinja2 version, since it is not available in
# current  version on pypi
def test_equalto(value,other):
    return value==other

def test_startswith(value,other):
    return value.startswith(other)

def test_in(value,other):
    return value in other

def test_contains_from(values,other):
    if not values:
        return False
    else:
        return any([any([x is y for y in other]) for x in values])

def append_dict(d1,d2):
    return dict(d1.items()+d2.items())


def custom_replace(values,replacements):
    if not replacements:
        return values
    def repl(v):
        for to_replace, replace_with in replacements:
            if v is to_replace:
                return replace_with
        return v
    return map(repl,values)

def run_gams(model_file,work_dir,gams_exec=None):
    if not gams_exec:
        gams_exec = "gams"

    # Run GAMS and check return code
    print "Running GAMS on {} in {}".format(model_file,work_dir)
    try:
        p = sp.Popen([gams_exec,os.path.basename(model_file)],cwd=work_dir)
        p.wait()
        if p.returncode != 0:
            raise GamspyExecutionError("GAMS returned with an error. Return code is {}.".format(p.returncode))
    except WindowsError as e:
        if e.errno==2:
            raise GamspyExeNotFoundError("The GAMS executable '{}' was not found.".format(gams_exec))
        else:
            raise

class GamspyExeNotFoundError(Exception):
    pass

class GamspyExecutionError(Exception):
    pass



j2env = {
        "filters": {"select_vtype":select_vtype,"custom_replace":custom_replace,"append_dict":append_dict},
        "tests": {"equalto":test_equalto,"startswith":test_startswith,"in":test_in,"contains_from":test_contains_from},
        "globals": {"enumerate":enumerate,"zip":zip}
    }