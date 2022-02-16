# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _call_, _str_

_dynapyt_ast_ = __file__ + ".orig"
try:
    a = _assign_(_dynapyt_ast_, 2, _str_(_dynapyt_ast_, 1, 'hello ' 'world'), [lambda: a])
    b = _assign_(_dynapyt_ast_, 4, _str_(_dynapyt_ast_, 3, f"testing {a}" f"and {a}"), [lambda: b])
    _call_(_dynapyt_ast_, 6, lambda: print(_str_(_dynapyt_ast_, 5, f'hello {a}'
       f'and {b}'
       'testing'
       'multiple')))
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)