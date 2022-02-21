# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _read_, _call_, _func_exit_, _assign_, _func_entry_

_dynapyt_ast_ = __file__ + ".orig"
try:
    class Y:
        pass
    
    class X(_read_(_dynapyt_ast_, 1, lambda: Y)):
        def __init__(self) -> None:
            _func_entry_(_dynapyt_ast_, 3, [lambda: self])
            _call_(_dynapyt_ast_, 2, lambda: super(X, self))
            _func_exit_(_dynapyt_ast_, 3)

    x = _assign_(_dynapyt_ast_, 6, _call_(_dynapyt_ast_, 5, lambda: _read_(_dynapyt_ast_, 4, lambda: X)()), [lambda: x])
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)