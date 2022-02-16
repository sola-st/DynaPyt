class A:
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
x.a.d[x.b(1)] = 5