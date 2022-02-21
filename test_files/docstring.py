# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _attr_, _str_, _func_exit_, _func_entry_, _call_, _read_

_dynapyt_ast_ = __file__ + ".orig"
try:
    def foo():
        """
    This is
    the description
    for foo()
    """
        _func_entry_(_dynapyt_ast_, 3, [])
        _call_(_dynapyt_ast_, 2, lambda: print(_str_(_dynapyt_ast_, 1, 'test')))
        _func_exit_(_dynapyt_ast_, 3)
    
    _call_(_dynapyt_ast_, 5, lambda foo = foo: _read_(_dynapyt_ast_, 4, lambda foo = foo: foo)())
    _call_(_dynapyt_ast_, 8, lambda foo = foo: print(_attr_(_dynapyt_ast_, 7, _read_(_dynapyt_ast_, 6, lambda foo = foo: foo), "__doc__")))
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)