# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _binary_op_
from dynapyt.runtime import _unary_op_
from dynapyt.runtime import _literal_
from dynapyt.runtime import _condition_
from dynapyt.runtime import _func_entry_
from dynapyt.runtime import _func_exit_

_dynapyt_source_code_ = """
def foo(x):
    x += 2
    if x < 2:
        return x
    else:
        return x-2

class X:
    def bar(x, y):
        if x < y:
            return x
        else:
            return y
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    def foo(x):
        _func_entry_(9)
        x += _literal_(2, 2)
        if _condition_(8, x < _literal_(3, 2)):
            return _func_exit_(4, x)
        else:
            return _func_exit_(7, _binary_op_(6, x, "Subtract", _literal_(5, 2)))

    class X:
        def bar(x, y):
            _func_entry_(13)
            if _condition_(12, x < y):
                return _func_exit_(10, x)
            else:
                return _func_exit_(11, y)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)