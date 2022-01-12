# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _assign_, _binary_op_, _unary_op_, _call_, _literal_, _read_var_, _condition_, _jump_, _func_entry_, _func_exit_

_dynapyt_source_code_ = """
foo(1, 2)
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    _call_(4, lambda: foo(1, 2))
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)