class ContextManagerOne:

    def __enter__(self):
        print('ContextManagerOne: __enter__')
        return "context manager one"

    def __exit__(self, exc_type, exc_value, traceback):
        print('ContextManagerOne: __exit__')
        print("exc_type: ", exc_type)
        print("exc_value: ", exc_value)
        return True

class ContextManagerTwo:
    
    def __enter__(self):
        print('ContextManagerTwo: __enter__')
        return "context manager two"

    def __exit__(self, exc_type, exc_value, traceback):
        print('ContextManagerTwo: __exit__')
        print("exc_type: ", exc_type)
        print("exc_value: ", exc_value)
        return True

try :    
    with ContextManagerOne() as cm1, ContextManagerTwo() as cm2:
        print('inside with block')
        print(cm1)
        print(cm2)
        raise Exception("exception raised inside with statement block")
except Exception as e:
    print("exception caught: ", e)
else:
    print("no exception raised")