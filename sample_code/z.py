# tracer: DO NOT INSTRUMENT

from nativetracer.trc import _trace_all_
from sys import settrace

def _native_tracer_run_():
    a = 1
    b = 2
    c = a + b
    
    def foo(x):
        return x+x
    
    d = foo(c)
settrace(_trace_all_)
_native_tracer_run_()