def decorator_function_one(func):
    def wrapper():
        print("Decorator function before")
        func()
        print("Decorator function after")
    return wrapper

@decorator_function_one
def return_number():
    number = 2
    print("Number returned from function: ", number)
    return number

result = return_number()
print("Number returned from decorated function: ", result)


