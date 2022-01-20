import numbers
import string
import logging
from typing import Any, List, Optional, Tuple, Union
import libcst as cst
from .BaseAnalysis import BaseAnalysis

class TraceAll(BaseAnalysis):
    
    def __init__(self) -> None:
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def log(self, *args):
        res = ''
        for arg in args:
            res += ' ' + str(arg)
        logging.info(res)

    # Literals

    def number(self, iid: int, val: Any) -> Any:
        self.log('    Number', 'value:', val)
    
    def string(self, iid: int, val: Any) -> Any:
        self.log('    String', 'value:', val[:15] + '...')
    
    def boolean(self, iid: int, val: Any) -> Any:
        self.log('    Boolean', 'value:', val)
    
    def literal(self, iid: int, val: Any) -> Any:
        self.log('Literal   ', 'value:', val)
        if isinstance(val, numbers.Number):
            self.number(iid, val)
        elif isinstance(val, str):
            self.string(iid, val)
        return val

    # Variables
    
    def read_var(self, iid: int, name: str, val: Any, is_global: bool) -> Any:
        pass

    def write_var(self, iid: int, name: str, old_val: Any, new_val: Any, is_global: bool) -> Any:
        pass

    def delete_var(self, iid: int, name: str, val: Any, is_global: bool) -> None:
        pass

    # Attributes

    def read_attr(self, iid: int, name: str, val: Any, base_obj: Any) -> Any:
        pass

    def write_attr(self, iid: int, name: str, old_val: Any, new_val: Any, base_obj: Any) -> Any:
        pass

    def delete_attr(self, iid: int, name: str, val: Any, base_obj: Any) -> None:
        pass

    # Expressions

    def binary_op(self, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        self.log('Binary Operation', left, op, right, '->', result)

    def unary_op(self, iid: int, op: str, arg: Any, result: Any) -> Any:
        self.log('Unary Operation', op, arg, '->', result)

    def comparison(self, iid: int, left: Any, right_list: List[Any], result: Any) -> Any:
        self.log('Comparison', left, right_list, '->', result)

    # Instrumented function
    
    def func_enter(self, iid: int, f: str, base: Any, args: List[Any], is_constructor: bool, function_iid: int, function_sid: str) -> None:
        pass

    def func_exit(self, iid: int, f: str, base: Any, args: List[Any], result: Any, is_constructor: bool, function_iid: int, function_sid: str) -> Any:
        pass

    # Subscripts

    def read_sub(self, iid: int, name: str, val: Any, slices: List[Tuple[int, int]]) -> Any:
        pass

    def write_sub(self, iid: int, name: str, old_val: Any, new_val: Any, slices: List[Tuple[int, int]]) -> Any:
        pass
    
    def delete_sub(self, iid: int, name: str, val: Any, slices: List[Tuple[int, int]]) -> None:
        pass

    # Function Call

    def pre_call(self, iid: int):
        self.log('Before function call at', iid)
    
    def post_call(self, iid: int):
        self.log('After function call at', iid)

    # Statements

    def assignment(self, iid: int, op: str, left: Any, right: Any) -> Any:
        pass

    def raise_stmt(self, iid: int, type: Exception) -> Optional[Exception]:
        pass

    def assert_stmt(self, iid: int, condition: bool, message: str) -> Optional[bool]:
        pass

    def pass_stmt(self, iid: int) -> None:
        pass

    # Imports

    def import_stmt(self, iid: int, name: str, module: str, alias: str) -> None:
        pass

    # Control flow
    
    def if_stmt(self, iid: int, cond_value: bool) -> Optional[bool]:
        pass

    def for_stmt(self, iid: int, cond_value: bool, is_async: bool) -> Optional[bool]:
        pass

    def while_stmt(self, iid: int, cond_value: bool) -> Optional[bool]:
        pass

    def break_stmt(self, iid: int, goto_iid: int) -> Optional[bool]:
        pass

    def continue_stmt(self, iid: int, goto_iid: int) -> Optional[bool]:
        pass

    def try_stmt(self, iid: int) -> None:
        pass

    def exception_stmt(self, iid: int, exceptions: List[Exception], caught: Exception) -> Optional[Exception]:
        pass

    # With

    def with_stmt(self, iid: int, items: List[Tuple[Any, str]], is_async: bool) -> Optional[List[Tuple[Any, str]]]:
        pass

    # Function definitions

    def function_def(self, iid: int, name: str, args: List[cst.Arg], decorators: List[cst.Decorator], returns: List[Any], is_async:bool) -> None: # name is None for lambda functions
        pass

    def function_arg(self, iid: int, name: str, default: Any, annotation: cst.Annotation) -> None:
        pass

    def return_stmt(self, iid: int, function_iid: int, value: Any) -> Any:
        pass

    def yield_stmt(self, iid: int, function_iid: int, value: Any) -> Any:
        pass

    # Global

    def global_declaration(self, iid: int, names: List[str]) -> None:
        pass

    def nonlocal_declaration(self, iid: int, names: List[str]) -> None:
        pass

    # Class definitions

    def class_def(self, iid: int, name: str, bases: List[Any], decorators: List[cst.Decorator], meta_classes: List[Any]) -> None:
        pass

    # Await

    def await_stmt(self, iid: int, waiting_for: Any) -> Any:
        pass

    # Top level

    def module(self, iid: int) -> None:
        pass

    def expression(self, iid: int, value: Any) -> Any:
        pass

    def statement(self, iid: int) -> None:
        pass