# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _binary_op_
from dynapyt.runtime import _unary_op_

x = _binary_op_(2, 1, "Add", 2, lambda: 1 + 2)
n = 6

m = [1, _unary_op_(3, "Minus", 2, lambda: -2), 3, 4, 5, 6]

def foo(bar):
    return _binary_op_(5, _binary_op_(4, 1, "Add", bar, lambda bar = bar: 1 + bar), "Add", 2, lambda bar = bar: 1 + bar + 2)

for i in range(int(_binary_op_(6, n, "Divide", 2, lambda n = n: n/2))):
    print(m[i])
    y = m[i:_binary_op_(7, 2, "Multiply", i, lambda i = i: 2*i)]
