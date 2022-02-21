import logging
from types import TracebackType
from typing import Any, List, Optional, Tuple, Union
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location

class TraceAll(BaseAnalysis):
    
    def __init__(self) -> None:
        super().__init__()
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def log(self, iid: int, *args):
        self.__log(iid, ':', args)

    # Literals

    def number(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Number', 'value:', val)
    
    def string(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    String', 'value:', val)
    
    def boolean(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Boolean', 'value:', val)
    
    def literal(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, 'Literal   ', 'value:', val)

    # Memory access

    def mem_access(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, 'Accessing', '->', val)
    
    def read(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Reading', '->', val)

    def write(self, dyn_ast: str, iid: int, old_val: Any, new_val: Any) -> Any:
        self.log(iid, '    Writing', '->', new_val, '(old:', old_val, ')')

    def delete(self, dyn_ast: str, iid: int, val: Any) -> Optional[bool]:
        self.log(iid, '    Deleting', '->', val)

    def attribute(self, dyn_ast: str, iid: int, base: Any, name: str, val: Any) -> Any:
        self.log(iid, 'Attribute', name, 'of', base, '->', val)
    
    def subscript(self, dyn_ast: str, iid: int, base: Any, slice: List[Union[int, Tuple]], val: Any) -> Any:
        self.log(iid, 'Slice', slice, 'of', base, '->', val)

    # Expressions

    def binary_op(self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, 'Binary Operation', left, op, right, '->', result)

    def unary_op(self, dyn_ast: str, iid: int, op: str, arg: Any, result: Any) -> Any:
        self.log(iid, 'Unary Operation', op, arg, '->', result)

    def comparison(self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, 'Comparison', left, op, right, '->', result)

    # Instrumented function

    def func_enter(self, dyn_ast: str, iid: int, args: List[Any]) -> None:
        ast = self.__get_ast(dyn_ast)
        if get_node_by_location(ast, self.iids.iid_to_location[iid], m.FunctionDef()).name in ['__str__', '__repr__']:
            self.danger_of_recursion = True
        self.log(iid, 'Entered function', 'with arguments', args)

    def func_exit(self, dyn_ast: str, iid: int, result: Any) -> Any:
        ast = self.__get_ast(dyn_ast)
        if get_node_by_location(ast, self.iids.iid_to_location[iid], m.FunctionDef()).name in ['__str__', '__repr__']:
            self.danger_of_recursion = True
        self.log(iid, 'Exiting function', '->', result)
    
    def return_stmt(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, '   Returning', value)

    def yield_stmt(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, '   Yielding', value)

    # Function Call

    def pre_call(self, dyn_ast: str, iid: int):
        self.log(iid, 'Before function call')
    
    def post_call(self, dyn_ast: str, iid: int):
        self.log(iid, 'After function call')

    # Statements

    def assignment(self, dyn_ast: str, iid: int, left: List[Any], right: Any) -> Any:
        self.log(iid, 'Assignment', left, '->', right)
    
    def augmented_assignment(self, dyn_ast: str, iid: int, left: Any, op: str, right: Any) -> Any:
        self.log(iid, 'Augmented assignment', left, op, right)

    def raise_stmt(self, dyn_ast: str, iid: int, exc: Exception) -> Optional[Exception]:
        self.log(iid, 'Exception raised', exc)

    def assert_stmt(self, dyn_ast: str, iid: int, condition: bool, message: str) -> Optional[bool]:
        pass

    # Imports

    def import_stmt(self, dyn_ast: str, iid: int, name: str, module: str, alias: str) -> None:
        pass

    # Control flow

    def enter_ctrl_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, 'Control-flow enter', 'with condition', cond_value)
    
    def exit_ctrl_flow(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Control-flow exit')

    def if_stmt(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, '   If', cond_value)

    def for_stmt(self, dyn_ast: str, iid: int, cond_value: bool, is_async: bool) -> Optional[bool]:
        self.log(iid, '   For', cond_value)

    def while_stmt(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, '   While', cond_value)

    def break_stmt(self, dyn_ast: str, iid: int) -> Optional[bool]:
        self.log(iid, 'Break')

    def continue_stmt(self, dyn_ast: str, iid: int) -> Optional[bool]:
        self.log(iid, 'Continue')

    def try_stmt(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Entered try')

    def exception_stmt(self, dyn_ast: str, iid: int, exceptions: List[Exception], caught: Exception) -> Optional[Exception]:
        self.log(iid, 'Caught', caught, 'from', exceptions)

    # With

    def with_stmt(self, dyn_ast: str, iid: int, items: List[Tuple[Any, str]], is_async: bool) -> Optional[List[Tuple[Any, str]]]:
        pass

    # Function definitions

    def function_def(self, dyn_ast: str, iid: int, name: str, args: List[cst.Arg], decorators: List[cst.Decorator], returns: List[Any], is_async:bool) -> None: # name is None for lambda functions
        pass

    def function_arg(self, dyn_ast: str, iid: int, name: str, default: Any, annotation: cst.Annotation) -> None:
        pass

    # Global

    def global_declaration(self, dyn_ast: str, iid: int, names: List[str]) -> None:
        pass

    def nonlocal_declaration(self, dyn_ast: str, iid: int, names: List[str]) -> None:
        pass

    # Class definitions

    def class_def(self, dyn_ast: str, iid: int, name: str, bases: List[Any], decorators: List[cst.Decorator], meta_classes: List[Any]) -> None:
        pass

    # Await

    def await_stmt(self, dyn_ast: str, iid: int, waiting_for: Any) -> Any:
        pass

    # Top level

    def module(self, dyn_ast: str, iid: int) -> None:
        pass

    def pre_expression(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Expression')

    def post_expression(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, 'Expression', '->', value)

    def statement(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Statement')

    def uncaught_exception(self, exc: Exception, stack_trace: TracebackType) -> None:
        self.log(-1, 'Uncaught exception', exc, stack_trace)
    
    def begin_execution(self) -> None:
        self.log(-1, 'Execution started')
    
    def end_execution(self) -> None:
        self.log(-1, 'Execution ended')