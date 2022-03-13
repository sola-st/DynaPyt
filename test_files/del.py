# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _str_, _int_, _attr_, _list_, _write_, _dict_, _delete_, _read_, _sub_, _call_

_dynapyt_ast_ = __file__ + ".orig"
try:
    a = _write_(_dynapyt_ast_, 5, _dict_(_dynapyt_ast_, 4, [(_str_(_dynapyt_ast_, 0, 'a'), _int_(_dynapyt_ast_, 1, 0)), (_str_(_dynapyt_ast_, 2, 'b'), _int_(_dynapyt_ast_, 3, 1))]), [lambda: a])
    b = _write_(_dynapyt_ast_, 37, _list_(_dynapyt_ast_, 36, [_int_(_dynapyt_ast_, 33, 1), _int_(_dynapyt_ast_, 34, 2), _int_(_dynapyt_ast_, 35, 3)]), [lambda: b])
    _call_(_dynapyt_ast_, 23, print(_read_(_dynapyt_ast_, 22, lambda: a)), True, None, None)
    _delete_(_dynapyt_ast_, 26, [(_read_(_dynapyt_ast_, 24, lambda: a), ['a'], True)])
    _delete_(_dynapyt_ast_, 28, [(_read_(_dynapyt_ast_, 38, lambda: b), "a", False)])
    _call_(_dynapyt_ast_, 15, print(_read_(_dynapyt_ast_, 14, lambda: a)), True, None, None)
    _call_(_dynapyt_ast_, 31, print(_read_(_dynapyt_ast_, 30, lambda: b)), True, None, None)
    _delete_(_dynapyt_ast_, 40, [(locals(), ["a"], True)])
    _call_(_dynapyt_ast_, 42, print(_read_(_dynapyt_ast_, 41, lambda: a)), True, None, None)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)