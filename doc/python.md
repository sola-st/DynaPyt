Class Attributes and Functions
==============================
Each function defined in a class does not have access to the identifiers inside the class. So
```
class X:
    a = 0
    def foo():
        print(a) # Error
    
    def bar():
        foo()    # Error
```

However, when the class body gets executed the method declarations are executed and hence
```
class X:
    a = 0
    def foo():
        print(a) # Error
    
    def bar(foo=foo):
        foo()    # Works
```
.
