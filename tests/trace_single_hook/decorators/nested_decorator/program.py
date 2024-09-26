def decorator_function_one(func):
    def wrapper_one():
        print("Decorator function one: before")
        result = func()
        print("Decorator function one: after")
        return result + 1
    return wrapper_one

def decorator_function_two(func):
    def wrapper_two():
        print("Decorator function two: before")
        result = func()
        print("Decorator function two: after")
        return result
    return wrapper_two

@decorator_function_two
@decorator_function_one
def simple_function():
    print("Inside simple function")
    return 1

print(simple_function())

