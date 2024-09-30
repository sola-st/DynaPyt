from contextlib import contextmanager

@contextmanager
def my_context_manager():
    print('Entering context')
    yield
    print('Exiting context')

with my_context_manager():
    print('Inside context')

    

