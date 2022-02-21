# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _func_entry_, _assign_, _read_, _int_, _call_, _func_exit_

_dynapyt_ast_ = __file__ + ".orig"
try:
    class X:
        a = _assign_(_dynapyt_ast_, 2, _int_(_dynapyt_ast_, 1, 0), [lambda: a])
        b = _assign_(_dynapyt_ast_, 4, _read_(_dynapyt_ast_, 3, lambda a = a: a), [lambda: b])
        n = _assign_(_dynapyt_ast_, 10, _call_(_dynapyt_ast_, 9, lambda a = a: repr((_read_(_dynapyt_ast_, 5, lambda a = a: a), (_int_(_dynapyt_ast_, 6, 0) for i in _call_(_dynapyt_ast_, 8, lambda: range(_int_(_dynapyt_ast_, 7, 10))))))), [lambda: n])
        def __init__(self) -> None:
            _func_entry_(_dynapyt_ast_, 15, [lambda self = self: self])
            self.c = _assign_(_dynapyt_ast_, 12, _int_(_dynapyt_ast_, 11, 0), [lambda: self.c])
            _call_(_dynapyt_ast_, 14, lambda: print(_int_(_dynapyt_ast_, 13, 0)))
            _func_exit_(_dynapyt_ast_, 15)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)