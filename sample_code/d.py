# class X:
def bar(x):
    res = x
    return res

def foo(x):
    print('test')
    return x+1

bar = lambda: foo(2) + foo(3) + bar(4)
bar()