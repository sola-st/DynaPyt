# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _attr_, _str_, _read_, _tuple_, _int_, _dict_, _call_, _gen_, _assign_

_dynapyt_ast_ = __file__ + ".orig"
try:
    a = _assign_(_dynapyt_ast_, 6, _dict_(_dynapyt_ast_, 5, [(_str_(_dynapyt_ast_, 1, 'a'), _int_(_dynapyt_ast_, 2, 1)), (_str_(_dynapyt_ast_, 3, 'b'), _int_(_dynapyt_ast_, 4, 0))]), [lambda: a])
    b = _assign_(_dynapyt_ast_, 15, _dict_(_dynapyt_ast_, 14, [(_read_(_dynapyt_ast_, 7, lambda: c), _read_(_dynapyt_ast_, 8, lambda: d)) for c, d in _gen_(_dynapyt_ast_, 13, _call_(_dynapyt_ast_, 12, _attr_(_dynapyt_ast_, 11, _read_(_dynapyt_ast_, 10, lambda: a), "items"), False, [], {}))]), [lambda: b])
    _call_(_dynapyt_ast_, 17, print(_read_(_dynapyt_ast_, 16, lambda: a)), True, None, None)
    _call_(_dynapyt_ast_, 19, print(_read_(_dynapyt_ast_, 18, lambda: b)), True, None, None)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)