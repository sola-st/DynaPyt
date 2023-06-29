def bar(x):
    print(f"bar {x}")
    return x


foo = bar("yes") if 23 == 23 else bar("no")
print(foo)
foo = bar("yes") if 20 == 23 else bar("no")
print(foo)
