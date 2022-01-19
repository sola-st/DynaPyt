# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _call_, _literal_, _read_var_, _condition_, _enter_ctrl_flow_, _exit_ctrl_flow_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
i = 0
while i < 10:
    i += 1
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    i = _assign_(3, _literal_(2, 0))
    while _enter_ctrl_flow_(8, _read_var_(4, lambda: i) < _literal_(5, 10)):
        i += _assign_(7, [i], _literal_(6, 1), 0)
    else:
        _exit_ctrl_flow_(8)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)