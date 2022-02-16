# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _call_

_dynapyt_source_code_ = "def foo():\n    print('foo')\n    bar()\n\ndef bar():\n    print('bar')\n\ndef spam():\n    print('spam')\n    foo()\n\nspam()"
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    def foo():
        _call_(_dynapyt_ast_, 1, lambda: print('foo'))
        _call_(_dynapyt_ast_, 2, lambda: bar())
    
    def bar():
        _call_(_dynapyt_ast_, 3, lambda: print('bar'))
    
    def spam():
        _call_(_dynapyt_ast_, 4, lambda: print('spam'))
        _call_(_dynapyt_ast_, 5, lambda: foo())
    
    _call_(_dynapyt_ast_, 6, lambda: spam())
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)