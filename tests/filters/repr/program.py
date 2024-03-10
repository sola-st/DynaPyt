class X:
    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        return "X"


x = X()
print(repr(x))
