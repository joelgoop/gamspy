import numpy as np
cimport numpy as cnp


cpdef object set_from_1d_array(object db,char* name,cnp.ndarray elements):
    cdef object out_set = db.add_set(name,1,"")
    cdef object element
    for element in elements:
        out_set.add_record(element)
    return out_set

cpdef object set_from_2d_array(object db,char* name,cnp.ndarray elements):
    cdef object out_set = db.add_set(name,elements.shape[1],"")
    cdef cnp.ndarray row
    for row in elements:
        out_set.add_record(tuple(row))
    return out_set

cpdef object param_from_2d_array(object db,char* name,cnp.ndarray row_set,cnp.ndarray col_set, cnp.ndarray[cnp.float64_t, ndim=2] values):
    cdef object out_param = db.add_parameter(name,2,"")
    cdef cnp.int64_t i,j
    cdef cnp.float64_t val
    for (i, j), val in np.ndenumerate(values):
        out_param.add_record((row_set[i],col_set[j])).value = val
    return out_param

cpdef object param_from_1d_array(object db,char* name,cnp.ndarray set_list,cnp.ndarray[cnp.float64_t, ndim=2] values):
    cdef object out_param = db.add_parameter(name,1,"")
    cdef cnp.int64_t i,j
    cdef cnp.float64_t val
    for (i,j),val in np.ndenumerate(values):
        out_param.add_record((set_list[i],)).value = val
    return out_param


cpdef dict parse_along(dict to_parse, list args_keep, list arg_parsealong):
    cdef dict out = {}
    cdef str key,parsed_arg
    cdef cnp.int64_t i
    cdef cnp.ndarray tmp
    for key in args_keep:
        tmp = cnp.zeros((len(arg_parsealong),1))
        for i,parsed_arg in enumerate(arg_parsealong):
            tmp[i] = to_parse[(key,parsed_arg)]
        out[key] = tmp
    return out

cpdef cnp.ndarray parse_along_1d(dict to_parse, list args):
    cdef cnp.int64_t i,j
    cdef cnp.float64_t dummy
    cdef cnp.ndarray tmp = np.zeros((len(args),1))
    for (i,j),dummy in np.ndenumerate(tmp):
        try:
            tmp[i,0] = to_parse[(args[i],)]
        except KeyError as e:
            print "{} was not found.".format(args[i])
    return tmp

cpdef cnp.ndarray parse_along_2d(dict to_parse, list args1, list args2):
    cdef cnp.int64_t i,j
    cdef cnp.float64_t dummy
    cdef cnp.ndarray tmp = np.zeros((len(args1),len(args2)))
    for (i,j),dummy in np.ndenumerate(tmp):
        try:
            tmp[i,j] = to_parse[(args1[i],args2[j])]
        except KeyError as e:
            print "{},{} was not found.".format(args1[i],args2[j])
    return tmp