# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _assert_

_dynapyt_ast_ = __file__ + ".orig"
try:
    assert _assert_(_dynapyt_ast_, 1, (0==0), None)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)