import a


def foo():
    print("foo")


def bar():
    foo()
    a.hello_world()


def baz(x: int):
    if x > 10:
        foo()
    else:
        bar()


baz(5)
