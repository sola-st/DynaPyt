import logging
from types import TracebackType
from typing import Any, Dict, List, Optional, Tuple, Union
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location

class TraceAll(BaseAnalysis):
    
    def __init__(self) -> None:
        super().__init__()
        self.danger_of_recursion = False
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def log(self, iid: int, *args):
        res = ''
        for arg in args:
            if self.danger_of_recursion:
                res += ' ' + str(hex(id(arg)))
            else:
                res += ' ' + str(arg)
        logging.info(str(iid) + ': ' + res[:80])

    # Literals

    def number(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Number', 'value:', val)
    
    def integer(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Integer', 'value:', val)
    
    def _float(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Float', 'value:', val)
    
    def imaginary(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Imaginary', 'value:', val)
    
    def string(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    String', 'value:', val)
    
    def boolean(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Boolean', 'value:', val)
    
    def literal(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, 'Literal   ', 'value:', val)
    
    def dictionary(self, dyn_ast: str, iid: int, items: List[Any], value: Dict) -> Dict:
        self.log(iid, 'Dictionary', 'items:', items)
    
    def _list(self, dyn_ast: str, iid: int, value: List) -> List:
        self.log(iid, 'List', value)
    
    def _tuple(self, dyn_ast: str, iid: int, items: List[Any], value: tuple) -> tuple:
        self.log(iid, 'Tuple', 'items:', items)
    
    # Operations

    def operation(self, dyn_ast: str, iid: int, operator: str, operands: List[Any], result: Any) -> Any:
        pass

    def binary_operation(self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, 'Binary Operation', left, op, right, '->', result)

    def unary_operation(self, dyn_ast: str, iid: int, op: str, arg: Any, result: Any) -> Any:
        self.log(iid, 'Unary Operation', op, arg, '->', result)

    def comparison(self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, 'Comparison', left, op, right, '->', result)

    # Memory access

    def memory_access(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, 'Accessing')
    
    def read_identifier(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, '    Reading')

    def write(self, dyn_ast: str, iid: int, old_val: Any, new_val: Any) -> Any:
        self.log(iid, '    Writing')

    def delete(self, dyn_ast: str, iid: int, val: Any) -> Optional[bool]:
        self.log(iid, '    Deleting')

    def read_attribute(self, dyn_ast: str, iid: int, base: Any, name: str, val: Any) -> Any:
        self.log(iid, 'Attribute', name)
    
    def read_subscript(self, dyn_ast: str, iid: int, base: Any, sl: List[Union[int, Tuple]], val: Any) -> Any:
        self.log(iid, 'Slice', sl)

    # Instrumented function

    def function_enter(self, dyn_ast: str, iid: int, args: List[Any]) -> None:
        ast, iids = self._get_ast(dyn_ast)
        if get_node_by_location(ast, iids.iid_to_location[iid], m.FunctionDef()).name in ['__str__', '__repr__']:
            self.danger_of_recursion = True
        self.log(iid, 'Entered function', 'with arguments', args)

    def function_exit(self, dyn_ast: str, iid: int, result: Any) -> Any:
        ast, iids = self._get_ast(dyn_ast)
        if get_node_by_location(ast, iids.iid_to_location[iid], m.FunctionDef()).name in ['__str__', '__repr__']:
            self.danger_of_recursion = True
        self.log(iid, 'Exiting function', '->', result)
    
    def _return(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, '   Returning', value)

    def _yield(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, '   Yielding', value)

    # Function Call

    def pre_call(self, dyn_ast: str, iid: int, pos_args: Tuple, kw_args: Dict):
        self.log(iid, 'Before function call')
    
    def post_call(self, dyn_ast: str, iid: int, val: Any, pos_args: Tuple, kw_args: Dict):
        self.log(iid, 'After function call')

    # Statements
    
    def augmented_assignment(self, dyn_ast: str, iid: int, left: Any, op: str, right: Any) -> Any:
        self.log(iid, 'Augmented assignment', left, op, right)

    def _raise(self, dyn_ast: str, iid: int, exc: Exception, cause: Any) -> Optional[Exception]:
        self.log(iid, 'Exception raised', exc, 'because of', cause)

    def _assert(self, dyn_ast: str, iid: int, condition: bool, message: str) -> Optional[bool]:
        self.log(iid, 'Asserting', condition, 'with message', message)

    # Control flow

    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, 'Control-flow enter', 'with condition', cond_value)
    
    def exit_control_flow(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Control-flow exit')

    def _if(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, '   If', cond_value)

    def _for(self, dyn_ast: str, iid: int, next_value: Any, is_async: bool) -> Optional[bool]:
        self.log(iid, '   For', next_value)

    def _while(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.log(iid, '   While', cond_value)

    def _break(self, dyn_ast: str, iid: int) -> Optional[bool]:
        self.log(iid, 'Break')

    def _continue(self, dyn_ast: str, iid: int) -> Optional[bool]:
        self.log(iid, 'Continue')

    def _try(self, dyn_ast: str, iid: int) -> None:
        self.log(iid, 'Entered try')

    def exception(self, dyn_ast: str, iid: int, exceptions: List[Exception], caught: Exception) -> Optional[Exception]:
        self.log(iid, 'Caught', caught, 'from', exceptions)

    # Top level

    def runtime_event(self, dyn_ast: str, iid: int) -> None:
        pass

    def uncaught_exception(self, exc: Exception, stack_trace: TracebackType) -> None:
        self.log(-1, 'Uncaught exception', exc, stack_trace)
    
    def begin_execution(self) -> None:
        self.log(-1, 'Execution started')
    
    def end_execution(self) -> None:
        self.log(-1, 'Execution ended')