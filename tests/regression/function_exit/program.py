def foo():
    x = 1
    return x


def bar(x):
    if x < 5:
        return x


a = foo()
b = bar(1)
b = bar(10)
