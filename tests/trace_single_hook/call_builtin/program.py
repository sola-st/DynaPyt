class Foo:
    def __init__(self, i):
        self.i = i


foo1 = Foo(1)
foo2 = type(foo1)(2)
