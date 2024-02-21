# DYNAPYT: DO NOT INSTRUMENT


import dynapyt.runtime as _rt

_dynapyt_ast_ = "/home/eghbalaz/Documents/PhD/Projects/DynaPyt/tests/test_coverage/multi_file/program2.py" + ".orig"
try:
    def foo(x):
        return x + 1
    
    
    def bar(x):
        return _rt._call_(_dynapyt_ast_, 2, foo, False, [("", x)], {}) * 2
except Exception as _dynapyt_exception_:
    _rt._catch_(_dynapyt_exception_)

