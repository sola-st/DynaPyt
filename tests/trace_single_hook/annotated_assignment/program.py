from typing import Optional


class X:
    def __init__(self):
        self.x: int = 10


a = 10
b: int = a
c = X()
c.y: str = "hello"
c.z: Optional[str] = None
