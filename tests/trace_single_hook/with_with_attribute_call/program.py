
from contextlib import contextmanager

class Foo:
    @contextmanager
    def bar(self):
        yield "hello world"

foo = Foo()
with foo.bar() as cm:
    print(cm)
