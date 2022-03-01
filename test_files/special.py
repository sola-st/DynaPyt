# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _func_entry_, _return_, _assign_, _binary_op_, _func_exit_, _read_, _call_, _int_

_dynapyt_ast_ = __file__ + ".orig"
try:
    def foo(x, y, z):
        _func_entry_(_dynapyt_ast_, 7, [lambda: x, lambda: y, lambda: z])
        return _return_(_dynapyt_ast_, 6, return_val = _binary_op_(_dynapyt_ast_, 5, lambda: _binary_op_(_dynapyt_ast_, 3, lambda: _read_(_dynapyt_ast_, 1, lambda: x), 0, lambda: _read_(_dynapyt_ast_, 2, lambda: y)), 0, lambda: _read_(_dynapyt_ast_, 4, lambda: z)))
        _func_exit_(_dynapyt_ast_, 7)
    
    a = _assign_(_dynapyt_ast_, 11, (_int_(_dynapyt_ast_, 8, 10),
        _int_(_dynapyt_ast_, 9, 20),
        _int_(_dynapyt_ast_, 10, 30)), [lambda: a])
    
    _call_(_dynapyt_ast_, 16, _read_(_dynapyt_ast_, 12, lambda: foo), False, [("", _int_(_dynapyt_ast_, 13, 1)), ("", _int_(_dynapyt_ast_, 14, 2)), ("", _int_(_dynapyt_ast_, 15, 3))], {})
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)