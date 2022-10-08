class A():
    a = -1

class X():
    __a = 0

    def foo(self):
        print(self.__a)

class Y(X):
    a = 1
    def __init__(self):
        super().__init__()

class Z(Y):
    def __init__(self):
        super().__init__()


z = Z()
z.foo()