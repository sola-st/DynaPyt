def decorator_function_one(func):
    def wrapper():
        print("Decorator function one: before")
        result = func()
        print("Decorator function one: after")
        return result + 1
    return wrapper

def decorator_function_two(func):
    def wrapper():
        print("Decorator function two: before")
        result = func()
        print("Decorator function two: after")
        return result
    return wrapper

@decorator_function_two
@decorator_function_one
def simple_function():
    print("Inside simple function")
    return 1

print(simple_function())

