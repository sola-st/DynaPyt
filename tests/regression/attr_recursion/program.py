import types


class EnhancedModule(types.ModuleType):
    def __bool__(self):
        return vars(self).get("__bool__", lambda: True)()

    def __getattribute__(self, attr):
        try:
            ret = super().__getattribute__(attr)
        except AttributeError:
            if attr.startswith("__") and attr.endswith("__"):
                raise
            getter = getattr(self, "__getattr__", None)
            if not getter:
                raise
            ret = getter(attr)
        return ret.fget() if isinstance(ret, property) else ret


x = EnhancedModule("x")
print(x)
