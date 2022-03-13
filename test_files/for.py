# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _exit_for_, _call_, _read_, _list_, _int_, _gen_

_dynapyt_ast_ = __file__ + ".orig"
try:
    def g(n):
        for i in _gen_(_dynapyt_ast_, 3, _call_(_dynapyt_ast_, 1, range(_read_(_dynapyt_ast_, 0, lambda: n)), True, None, None)):
            yield _read_(_dynapyt_ast_, 2, lambda: i)
        else:
            _exit_for_(_dynapyt_ast_, 3)

    for i in _gen_(_dynapyt_ast_, 8, _call_(_dynapyt_ast_, 5, range(_int_(_dynapyt_ast_, 4, 5)), True, None, None)):
        _call_(_dynapyt_ast_, 7, print(_read_(_dynapyt_ast_, 6, lambda: i)), True, None, None)
    else:
        _exit_for_(_dynapyt_ast_, 8)
    
    for i in _gen_(_dynapyt_ast_, 17, _list_(_dynapyt_ast_, 14, [_int_(_dynapyt_ast_, 9, 0), _int_(_dynapyt_ast_, 10, 1), _int_(_dynapyt_ast_, 11, 2), _int_(_dynapyt_ast_, 12, 3), _int_(_dynapyt_ast_, 13, 4)])):
        _call_(_dynapyt_ast_, 16, print(_read_(_dynapyt_ast_, 15, lambda: i)), True, None, None)
    else:
        _exit_for_(_dynapyt_ast_, 17)
    
    for i in _gen_(_dynapyt_ast_, 23, _call_(_dynapyt_ast_, 20, _read_(_dynapyt_ast_, 18, lambda: g), False, [("", _int_(_dynapyt_ast_, 19, 5))], {})):
        _call_(_dynapyt_ast_, 22, print(_read_(_dynapyt_ast_, 21, lambda: i)), True, None, None)
    else:
        _exit_for_(_dynapyt_ast_, 23)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)