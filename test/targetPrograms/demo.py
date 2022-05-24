# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _enter_if_

_dynapyt_ast_ = __file__ + ".orig"
try:
    a = 0
    if _enter_if_(_dynapyt_ast_, 0, a < 10):
        print('small')
    else:
        print('large')
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)
