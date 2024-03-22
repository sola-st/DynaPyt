def foo():
    x = yield from range(3)


for i in range(3):
    res = foo().__next__()
    print(res)
