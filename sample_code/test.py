class X:
    a = 1

    def foo(a=a):
        print(a)
    
    def bar(self):
        self.foo()
    
    baz = lambda: foo()
    baz()

x = X()
# print(x.bar())