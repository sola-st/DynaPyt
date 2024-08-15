class A:
    def __init__(self):
        self.a = 1

    def f(self):
        return self.a


class B(A):
    def __init__(self):
        super().__init__()
        self.b = 2

    def f(self):
        return super().f() + self.b


b = B()
b.f()

c = len(locals()) + len(globals())
