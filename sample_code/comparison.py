# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _comp_op_, _call_, _literal_, _read_var_, _condition_, _enter_ctrl_flow_, _exit_ctrl_flow_, _jump_, _func_entry_, _func_exit_

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
    if _enter_ctrl_flow_(10, _comp_op_(7, _read_var_(4, "a", lambda: a), [(5, _read_var_(5, "b", lambda: b)), (0, _read_var_(6, "c", lambda: c))])):
        _call_(9, lambda: print(1))
        _exit_ctrl_flow_(10)
    if _enter_ctrl_flow_(17, _comp_op_(14, _read_var_(11, "a", lambda: a), [(3, _call_(13, lambda: range(10)))])):
        _call_(16, lambda: print(2))
        _exit_ctrl_flow_(17)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)