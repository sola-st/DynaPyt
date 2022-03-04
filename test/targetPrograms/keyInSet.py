# DYNAPYT: DO NOT INSTRUMENT

# https://docs.quantifiedcode.com/python-anti-patterns/performance/using_key_in_list_to_check_if_key_is_contained_in_a_list.html


from dynapyt.runtime import _catch_
from dynapyt.runtime import _comp_op_

_dynapyt_ast_ = __file__ + ".orig"
try:
    l = set([-i for i in range(1000)])
    
    res = 0
    
    for i in range(0, 2000, 7):
        if _comp_op_(_dynapyt_ast_, 0, -i, [(3, l)]):
            res += 1
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)