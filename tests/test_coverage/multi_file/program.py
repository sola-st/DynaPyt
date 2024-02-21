from .program2 import bar


def baz(x):
    return bar(x) ** 3


print(baz(2))
