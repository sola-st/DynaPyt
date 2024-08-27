a = [1, 2, 3]
b = [4, 5, 6]
print(list(zip(a, b)))
c, d = zip(*zip(a, b))
print(c)
print(d)
