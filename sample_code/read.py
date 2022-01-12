# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _literal_, _read_var_, _condition_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
a = 1
b = a
c = range(a)
d = a + b
for i in range(a):
    if i < d:
        break
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    a = _assign_(3, [a], _literal_(2, 1))
    b = _assign_(5, [b], _read_var_(4, lambda: a))
    c = _assign_(7, [c], range(_read_var_(6, lambda: a)))
    d = _assign_(11, [d], _binary_op_(10, _read_var_(8, lambda: a), "Add", _read_var_(9, lambda: b)))
    for i in range(_read_var_(12, lambda: a)):
        if _condition_(16, _read_var_(13, lambda: i) < _read_var_(14, lambda: d)):
            if _jump_(15, True):
                break
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)