# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _call_, _literal_, _read_var_, _condition_, _enter_ctrl_flow_, _exit_ctrl_flow_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
a = 10
if a > 0:
    a = 0
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    a = _assign_(3, _literal_(2, 10))
    if _enter_ctrl_flow_(8, _read_var_(4, lambda: a) > _literal_(5, 0)):
        a = _assign_(7, _literal_(6, 0))
        _exit_ctrl_flow_(8)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)