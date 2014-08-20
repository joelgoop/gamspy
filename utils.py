import tempfile
import shutil
import contextlib

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


j2env = {
        "filters": {"select_vtype":select_vtype,"custom_replace":custom_replace,"append_dict":append_dict},
        "tests": {"equalto":test_equalto,"startswith":test_startswith,"in":test_in,"contains_from":test_contains_from},
        "globals": {"enumerate":enumerate,"zip":zip}
    }