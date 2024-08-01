class DeferredError:
    def __init__(self, ex: BaseException):
        self.ex = ex

    def __getattr__(self, elt: str) -> None:
        raise self.ex

    @staticmethod
    def new(ex: BaseException):
        """
        Creates an object that raises the wrapped exception ``ex`` when used.
        """
        return DeferredError(ex)


def deferred_error() -> None:
    thing = DeferredError.new(ValueError("Some error text"))
    print("OK")
    x = thing.some_attr
    print("Not OK")


deferred_error()
