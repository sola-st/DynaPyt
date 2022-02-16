# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _call_, _lambda_, _func_entry_, _assign_, _int_, _read_, _func_exit_, _attr_, _binary_op_

_dynapyt_source_code_ = """class A:
    def __init__(self):
        self.c = 0
        self.d = [0, 1, 2]

class X:
    def __init__(self):
        self.a = 0
        self.b = lambda i: i*2

x = X()
y = x.a
x.a = A()
z = x.a.c
zz = x.b(2)
x.a.d[x.b(1)] = 5"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    class A:
        def __init__(self):
            _func_entry_(8, [self])
            self.c = _assign_(3, _int_(2, 0), [lambda: self.c])
            self.d = _assign_(7, [_int_(4, 0), _int_(5, 1), _int_(6, 2)], [lambda: self.d])
            _func_exit_(8)

    class X:
        def __init__(self):
            _func_entry_(16, [self])
            self.a = _assign_(10, _int_(9, 0), [lambda: self.a])
            self.b = _assign_(15, lambda i: _lambda_(14, [i], lambda: _binary_op_(13, _read_(11, lambda: i), 9, _int_(12, 2))), [lambda: self.b])
            _func_exit_(16)

    x = _assign_(19, _call_(18, lambda: _read_(17, lambda: X)()), [lambda: x])
    y = _assign_(22, _attr_(21, _read_(20, lambda: x), "a"), [lambda: y])
    x.a = _assign_(25, _call_(24, lambda: _read_(23, lambda: A)()), [lambda: x.a])
    z = _assign_(29, _attr_(28, _attr_(27, _read_(26, lambda: x), "a"), "c"), [lambda: z])
    zz = _assign_(34, _call_(33, lambda: _attr_(31, _read_(30, lambda: x), "b")(_int_(32, 2))), [lambda: zz])
    x.a.d[_call_(36, lambda: x.b(_int_(35, 1)))] = _assign_(38, _int_(37, 5), [lambda: x.a.d[_call_(36, lambda: x.b(_int_(35, 1)))]])
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)