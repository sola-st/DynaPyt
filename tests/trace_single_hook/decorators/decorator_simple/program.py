def decorator_function_one(func):
    def wrapper():
        print("Decorator function before")
        func()
        print("Decorator function after")
    return wrapper

@decorator_function_one
def simple_function():
    print("Simple function")

simple_function()

