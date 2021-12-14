# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _catch_
from dynapyt.runtime import _binary_op_
from dynapyt.runtime import _unary_op_
from dynapyt.runtime import _call_
from dynapyt.runtime import _literal_
from dynapyt.runtime import _read_var_

try:
    x = _binary_op_(4, _literal_(2, 1), "Add", _literal_(3, 2))
    n = _literal_(5, 6)
    a = _literal_(6, "test")
    b = _literal_(7, 3.141592)
    m = [_literal_(8, 1), _unary_op_(10, "Minus", _literal_(9, 2), lambda: -2), _literal_(11, 3), _literal_(12, 4), _literal_(13, 5), _literal_(14, 6)]
    
    def foo(bar):
        return _binary_op_(19, _binary_op_(17, _literal_(15, 1), "Add", _read_var_(16, lambda bar = bar: bar)), "Add", _literal_(18, 2))
    
    for i in _call_(26, lambda range = range, int = int, n = n: range(int(n/2))):
        _call_(30, lambda print = print, m = m, i = i: print(m[i]))
        _call_(37, lambda print = print, m = m, i = i: print(m[i:2*i]))
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)