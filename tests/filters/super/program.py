class X:
    def __getattribute__(self, name: str):
        res = super().__getattribute__(name)
        return res


x = X()
print(x.__class__)
