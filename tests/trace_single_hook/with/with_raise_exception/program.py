class ContextManager:

    def __enter__(self):
        print('__enter__')
        return "hello world"

    def __exit__(self, exc_type, exc_value, traceback):
        print('__exit__')
        print("exc_type: ", exc_type)
        print("exc_value: ", exc_value)

try :    
    with ContextManager() as cm:
        print('inside with block')
        print(cm)
        raise Exception("exception raised inside with statement block")
except Exception as e:
    print("exception caught: ", e)
else:
    print("no exception raised")