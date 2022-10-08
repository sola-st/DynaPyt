class X:
    a = 0
    b = a
    n = repr((a, (0 for i in range(10))))
    def __init__(self) -> None:
        self.c = 0
        print(0)