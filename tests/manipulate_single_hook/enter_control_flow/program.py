foo = [1,2,3]
if len(foo) > 2:
    print("true 1")
else:
    print("false 1")
    while foo is None:
        print("loop 2")
        foo.append(4)
        if len(foo) == 7:
            print("true 3")
            foo = None
print("end")