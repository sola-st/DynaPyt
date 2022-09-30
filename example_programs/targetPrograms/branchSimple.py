# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _enter_ctrl_flow_, _exit_ctrl_flow_

_dynapyt_ast_ = __file__ + ".orig"
try:
    a = 0
    while _enter_ctrl_flow_(_dynapyt_ast_, 2, a < 10):
        if _enter_ctrl_flow_(_dynapyt_ast_, 1, a % 2 == 0):
            print('even')
            _exit_ctrl_flow_(_dynapyt_ast_, 1)
        a += 1
    else:
        _exit_ctrl_flow_(_dynapyt_ast_, 2)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)
