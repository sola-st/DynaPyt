def decorator_function_one(func):
    def wrapper(*args):
        print("Decorator function before")
        func(*args)
        print("Decorator function after")
    return wrapper

@decorator_function_one
def simple_function(arg1, arg2):
    print("Simple function")
    print("parameter 1: ", arg1)
    print("parameter 2: ", arg2)

simple_function("foo", "bar")

