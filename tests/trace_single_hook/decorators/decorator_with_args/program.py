def decorator_function_with_args(arg1, arg2):
    def decorator_function(func):
        def wrapper():
            print("Decorator function before")
            func()
            print("Decorator function after")
        return wrapper
    return decorator_function

@decorator_function_with_args("arg1", "arg2")
def simple_function():
    print("Simple function")

simple_function()

