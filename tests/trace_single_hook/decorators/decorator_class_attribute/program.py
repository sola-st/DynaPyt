class foo:
    def decorator_func(self, func):
        def wrapper():
            print("Decorator function before")
            func()
            print("Decorator function after")
        return wrapper

f = foo()

@f.decorator_func
def simple_function():
    print("Simple function")

simple_function()