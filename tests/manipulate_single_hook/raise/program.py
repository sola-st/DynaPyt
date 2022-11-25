y = 4
try:
    if y > 3:
        raise KeyError("foo") from RuntimeError("bar") 
except TypeError:
    print("TypeError caught")
print("Done")