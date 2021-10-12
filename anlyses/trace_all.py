from typing import Any, List, Tuple, TypeVar
import libcst as cst

V = TypeVar('V')
V2 = TypeVar('V2')
V3 = TypeVar('V3')

class TraceAll():
    
    # Literals
    
    def literal(self, iid: str, val: V) -> V:
        return val

    # Variables
    
    def read_var(self, iid: str, name: str, val: V, is_global: bool) -> V:
        pass

    def write_var(self, iid: str, name: str, old_val: V, new_val: V2, is_global: bool) -> V2:
        pass

    def delete_var(self, iid: str, name: str, val: V, is_global: bool) -> V:
        pass

    # Attributes

    def read_attr(self, iid: str, name: str, val: V, base_obj: Any) -> V:
        pass

    def write_attr(self, iid: str, name: str, old_val: V, new_val: V2, base_obj: Any) -> V2:
        pass

    def delete_attr(self, iid: str, name: str, val: V, base_obj: Any) -> V:
        pass

    # Expressions

    def binary_op(self, iid: str, op: str, left: V, right: V, result: V) -> V:
        pass

    def unary_op(self, iid: str, op: str, arg: V, result: V) -> V:
        pass

    def compare(self, iid: str, op: str, left: V, right_list: List[V], result: V) -> V:
        pass

    def invoke_func_pre(self, iid: str, f: function, base: Any, args: List[V], is_constructor: bool, function_iid: str, function_sid: str) -> None:
        pass

    def invoke_func(self, iid: str, f: function, base: Any, args: List[V], result: V2, is_constructor: bool, function_iid: str, function_sid: str) -> V2:
        pass

    def conditional_jump(self, iid: str, condition: cst.BaseExpression, result: bool, goto_iid: str) -> Tuple[bool, str]:
        pass

    # Subscripts

    def read_sub(self, iid: str, name: str, val: V, slices: List[Tuple[int, int]]) -> V:
        pass

    def write_sub(self, iid: str, name: str, old_val: V, new_val: V2, slices: List[Tuple[int, int]]) -> V2:
        pass
    
    def delete_sub(self, iid: str, name: str, val: V, slices: List[Tuple[int, int]]) -> V:
        pass

    # Statements

    def assignment(self, iid: str, op: str, left: V, right: V2) -> V2:
        pass

    def print_stmt(self, iid: str, value: str) -> str:
        pass

    def raise_stmt(self, iid: str, type: Exception) -> Exception:
        pass

    def assert_stmt(self, iid: str, condition: cst.BaseExpression, message: str) -> Tuple[bool, str]:
        pass

    def pass_stmt(self, iid: str) -> None:
        pass

    # Imports

    def import_stmt(self, iid: str, name: str, module: str, alias: str) -> None:
        pass

    # Control flow
    
    def if_stmt(self, iid: str, condition: cst.BaseExpression, value: bool, body: cst.BaseStatement, else_body: cst.BaseStatement) -> Tuple[bool, cst.BaseStatement]:
        pass

    def for_stmt(self, iid: str, condition: cst.BaseExpression, value: bool, body: cst.BaseStatement, is_async: bool) -> Tuple[bool, cst.BaseStatement]:
        pass

    def while_stmt(self, iid: str, condition: cst.BaseExpression, value: bool, body: cst.BaseStatement) -> Tuple[bool, cst.BaseStatement]:
        pass

    def break_stmt(self, iid: str, goto_iid: str) -> str:
        pass

    def continue_stmt(self, iid: str, goto_iid: str) -> str:
        pass

    def try_stmt(self, iid: str) -> None:
        pass

    def exception_stmt(self, iid: str, exceptions: List[Exception], caught: Exception) -> Exception:
        pass

    # With

    def with_stmt(self, iid: str, items: List[Tuple[Any, str]], is_async: bool) -> None:
        pass

    # Function definitions

    def function_def(self, iid: str, name: str, args: List[cst.Arg], decorators: List[cst.Decorator], returns: List[Any], is_async:bool) -> None: # name is None for lambda functions
        pass

    def function_arg(self, iid: str, name: str, default: Any, annotation: cst.Annotation) -> None:
        pass

    def return_stmt(self, iid: str, function: function, value: V) -> V:
        pass

    def yield_stmt(self, iid: str, function: function, value: V) -> V:
        pass

    # Global

    def global_declaration(self, iid: str, names: List[str]) -> None:
        pass

    # Class definitions

    def class_def(self, iid: str, name: str, bases: List[Any], decorators: List[cst.Decorator], meta_classes: List[Any]) -> None:
        pass

    # Await

    def await_stmt(self, iid: str, waiting_for: cst.BaseExpression) -> None:
        pass

    # Top level

    def module(self, iid: str) -> None:
        pass

    def interactive(self, iid: str) -> None:
        pass

    def expression(self, iid: str) -> None:
        pass