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
import tempfile
import shutil
import contextlib
import subprocess as sp
import os
import errno


@contextlib.contextmanager
def make_tmp_dir():
    """Create a temporary directory for use in with-statement."""
    try:
        tmp_dir = tempfile.mkdtemp()
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)

def isnumber(val):
    """Test if val is a number by trying to cast to float."""
    try:
        float(val)
        return True
    except (ValueError,TypeError):
        return False

def select_vtype(variables,vtype):
    """Return a list of objects with attribute vtype=vtype"""
    return [var for var in variables if var.vtype==vtype]

def test_equalto(value,other):
    """Add equalto test from new jinja2 version, since it is not available in current  version on pypi."""
    return value==other

def test_startswith(value,other):
    """Test wrapping string.startswith"""
    return value.startswith(other)

def test_in(value,other):
    """Test if value is in other."""
    return value in other

def test_contains_from(values,other):
    """Test if other contains any object from values."""
    if not values:
        return False
    else:
        return any([any([x is y for y in other]) for x in values])

def append_dict(d1,d2):
    """Append d2 to d1 and return new dict."""
    return dict(d1.items()+d2.items())

def custom_replace(values,replacements):
    """Replace in values based on (to_replace,replace_with) pairs in replacements."""
    if not replacements:
        return values
    def repl(v):
        for to_replace, replace_with in replacements:
            if v is to_replace:
                return replace_with
        return v
    return map(repl,values)

def run_gams(model_file,work_dir,gams_exec=None):
    """Run gams executable."""
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
        if e.errno==errno.ENOENT:
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