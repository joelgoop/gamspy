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

def custom_replace(values,replacements):
    if not replacements:
        return values
    def repl(v):
        for to_replace, replace_with in replacements:
            if v is to_replace:
                return replace_with
        return v
    return map(repl,values)

def isnumber(val):
    try:
        float(val)
    except (ValueError,TypeError):
        return False
    return True

j2env = {
        "filters": {"select_vtype":select_vtype,"custom_replace":custom_replace},
        "tests": {"equalto":test_equalto,"startswith":test_startswith,"in":test_in},
        "globals": {"enumerate":enumerate,"zip":zip}
    }