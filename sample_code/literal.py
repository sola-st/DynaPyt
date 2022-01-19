# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _call_, _literal_, _read_var_, _condition_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
a = 10
b = True
c = 'test'
pi = 3.1415
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    a = _assign_(3, _literal_(2, 10))
    b = _assign_(5, _literal_(4, True))
    c = _assign_(7, _literal_(6, 'test'))
    pi = _assign_(9, _literal_(8, 3.1415))
    print(a, b, c, pi)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)