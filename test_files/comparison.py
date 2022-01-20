# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _call_, _comp_op_, _literal_, _read_var_, _assign_

_dynapyt_source_code_ = """
a = b = c = 5
if a < b == c:
    print(1)
if a in range(10):
    print(2)
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    a = b = c = _assign_(3, _literal_(2, 5))
    if _comp_op_(7, _read_var_(4, "a", lambda: a), [(5, _read_var_(5, "b", lambda: b)), (0, _read_var_(6, "c", lambda: c))]):
        _call_(9, lambda: print(_literal_(8, 1)))
    if _comp_op_(13, _read_var_(10, "a", lambda: a), [(3, _call_(12, lambda: range(_literal_(11, 10))))]):
        _call_(15, lambda: print(_literal_(14, 2)))
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)