# DYNAPYT: DO NOT INSTRUMENT


from dynapyt.runtime import _dynapyt_parse_to_ast_
from dynapyt.runtime import _catch_
from dynapyt.runtime import _binary_op_
from dynapyt.runtime import _unary_op_
from dynapyt.runtime import _literal_

_dynapyt_source_code_ = """
a = 10
if a > 0:
    a = 0
"""
_dynapyt_ast_ = _dynapyt_parse_to_ast_(_dynapyt_source_code_)
try:
    a = _literal_(2, 10)
    if _condition_(5, a > _literal_(3, 0)):
        a = _literal_(4, 0)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)