# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _read_, _int_, _unary_op_, _call_, _assign_, _func_exit_, _attr_, _func_entry_

_dynapyt_ast_ = __file__ + ".orig"
try:
    class A():
        a = _assign_(_dynapyt_ast_, 3, _unary_op_(_dynapyt_ast_, 2, 1, _int_(_dynapyt_ast_, 1, 1)), [lambda: a])
    
    class X():
        __a = _assign_(_dynapyt_ast_, 5, _int_(_dynapyt_ast_, 4, 0), [lambda: __a])

        def foo(self):
            _func_entry_(_dynapyt_ast_, 9, [lambda: self])
            _call_(_dynapyt_ast_, 8, lambda: print(_attr_(_dynapyt_ast_, 7, _read_(_dynapyt_ast_, 6, lambda: self), "__a")))
            _func_exit_(_dynapyt_ast_, 9)

    class Y(_read_(_dynapyt_ast_, 10, lambda: X)):
        a = _assign_(_dynapyt_ast_, 12, _int_(_dynapyt_ast_, 11, 1), [lambda: a])
        def __init__(self):
            _func_entry_(_dynapyt_ast_, 16, [lambda: self])
            _call_(_dynapyt_ast_, 15, lambda: _attr_(_dynapyt_ast_, 14, _call_(_dynapyt_ast_, 13, lambda: super(Y, self)), "__init__")())
            _func_exit_(_dynapyt_ast_, 16)

    class Z(_read_(_dynapyt_ast_, 17, lambda: Y)):
        def __init__(self):
            _func_entry_(_dynapyt_ast_, 21, [lambda: self])
            _call_(_dynapyt_ast_, 20, lambda: _attr_(_dynapyt_ast_, 19, _call_(_dynapyt_ast_, 18, lambda: super(Z, self)), "__init__")())
            _func_exit_(_dynapyt_ast_, 21)


    z = _assign_(_dynapyt_ast_, 24, _call_(_dynapyt_ast_, 23, lambda: _read_(_dynapyt_ast_, 22, lambda: Z)()), [lambda: z])
    _call_(_dynapyt_ast_, 27, lambda: _attr_(_dynapyt_ast_, 26, _read_(_dynapyt_ast_, 25, lambda: z), "foo")())
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)