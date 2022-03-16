# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _call_, _dict_, _int_, _write_, _str_, _read_

_dynapyt_ast_ = __file__ + ".orig"
try:
    def foo(*args, **kwargs):
        _call_(_dynapyt_ast_, 1, print(_read_(_dynapyt_ast_, 0, lambda: args)), True, None, None)
        _call_(_dynapyt_ast_, 3, print(_read_(_dynapyt_ast_, 2, lambda: kwargs)), True, None, None)
    
    _call_(_dynapyt_ast_, 8, _read_(_dynapyt_ast_, 4, lambda: foo), False, [("", _int_(_dynapyt_ast_, 5, 1)), ("", _int_(_dynapyt_ast_, 6, 2)), ("", _int_(_dynapyt_ast_, 7, 3))], {})
    _call_(_dynapyt_ast_, 13, _read_(_dynapyt_ast_, 9, lambda: foo), False, [], {"a": _int_(_dynapyt_ast_, 10, 1), "b": _int_(_dynapyt_ast_, 11, 2), "c": _int_(_dynapyt_ast_, 12, 3)})
    d = _write_(_dynapyt_ast_, 21, _dict_(_dynapyt_ast_, 20, [(_str_(_dynapyt_ast_, 14, 'a'), _int_(_dynapyt_ast_, 15, 1)), (_str_(_dynapyt_ast_, 16, 'b'), _int_(_dynapyt_ast_, 17, 2)), (_str_(_dynapyt_ast_, 18, 'c'), _int_(_dynapyt_ast_, 19, 3))]), [lambda: d])
    _call_(_dynapyt_ast_, 24, _read_(_dynapyt_ast_, 22, lambda: foo), False, [("**", _read_(_dynapyt_ast_, 23, lambda: d))], {})
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)