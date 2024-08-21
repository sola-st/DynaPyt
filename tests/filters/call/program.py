class X:
    def foo(self, x):
        print(x + x)


def foo(x):
    print(x)


def bar(x):
    print(2 * x)


foo("hello world")
bar(3)
x = X()
x.foo(4)
