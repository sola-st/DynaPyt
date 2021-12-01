# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _assign_

class X:
    def baz(x):
        res = _assign_(2, ['res'], lambda x = x: x)
        return res

    def foo(x):
        print('test')
        return x+1

    bar = _assign_(3, ['bar'], lambda foo = foo, baz = baz: foo(1) + foo(2) + baz(1))

X()