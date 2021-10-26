# DYNAPYT: DO NOT INSTRUMENT

from dynapyt.runtime import _assign_
from dynapyt.runtime import _expr_
from dynapyt.runtime import _binop_

x = _assign_(3, [x], a + b)

def foo(bar):
    return _binop_(5, _binop_(4, a, "Add", b, a + b), "Add", c, a + b + c)

for i in range(_binop_(6, n, "Multiply", 2, n*2)):
    _expr_(7, print(m[i]))
    y = _assign_(9, [y], m[i:2*i])
# comment
if g.name == 'Aryaz':
    g.test.x = _assign_(10, [g.test.x], 10)
    u = _assign_(11, [u], g.test.y)
