def g(n):
    for i in range(n):
        yield i

for i in range(5):
    print(i)

for i in [0, 1, 2, 3, 4]:
    print(i)

for i in g(5):
    print(i)