# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _literal_, _read_var_, _condition_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
for i in range(10):
    if i > 5:
        break
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    for i in _read_var_(2, lambda: range)(_literal_(3, 10)):
        if _condition_(7, _read_var_(4, lambda: i) > _literal_(5, 5)):
            if _jump_(6, True):
                break
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)