import logging
from types import TracebackType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location


class TraceAll(BaseAnalysis):
    """
    .. include:: ../../../docs/hooks.md
    """

    def __init__(self) -> None:
        super().__init__()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        handler = logging.FileHandler("output.log", "w", "utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(handler)

    def log(self, iid: int, *args, **kwargs):
        res = ""
        # for arg in args:
        #     if 'danger_of_recursion' in kwargs:
        #         res += ' ' + str(hex(id(arg)))
        #     else:
        #         res += ' ' + str(arg)
        logging.info(str(iid) + ": " + res[:80])

    # Literals

    def integer(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for integer literals.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the integer literal.

        Returns
        -------
        Any

            If provided, overwrites the value of the integer literal.
        """
        self.log(iid, "    Integer", "value:", val)

    def _float(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for floating point literals.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the floating point literal.

        Returns
        -------
        Any
            If provided, overwrites the value of the float literal.
        """
        self.log(iid, "    Float", "value:", val)

    def imaginary(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for imaginary number literals.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the imaginary number literal.


        Returns
        -------
        Any
            If provided, overwrites the value of the imaginary number literal.
        """
        self.log(iid, "    Imaginary", "value:", val)

    def string(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for string literals.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the string literal.

        Returns
        -------
        Any
            If provided, overwrites the value of the string literal.
        """
        self.log(iid, "    String", "value:", val)

    def boolean(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for boolean literals.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the boolean literal.


        Returns
        -------
        Any
            If provided, overwrites the value of the boolean literal.

        """
        self.log(iid, "    Boolean", "value:", val)

    def literal(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for all literals.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value of the literal.


        Returns
        -------
        Any
            If provided, overwrites the value of the literal.

        """
        self.log(iid, "Literal   ", "value:", val)

    def dictionary(self, dyn_ast: str, iid: int, items: List[Any], value: Dict) -> Dict:
        """Hook for a dictionary definition.

        E.g. `{'a': 1, 'b': 2}`
        or `{i: i for i in range(10)}`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        items : List[Any]
            The lis of key-value pairs.

        value : Dict
            The dictionary itself.


        Returns
        -------
        Dict
            If provided, overwrites the value of the dictionary.

        """
        self.log(iid, "Dictionary", "items:", items)

    def _list(self, dyn_ast: str, iid: int, value: List) -> List:
        """Hook for a list definition.

        E.g. `[1, 2, 3]`
        or `[i for i in range(10)]`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        value : List
            The list itself.


        Returns
        -------
        List
            If provided, overwrites the value of the list.

        """
        self.log(iid, "List", value)

    def _tuple(self, dyn_ast: str, iid: int, items: List[Any], value: tuple) -> tuple:
        """Hook for a tuple.

        E.g. `(1, 2, 3)`
        or `(i for i in range(10))`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        items : List[Any]
            The lis of items in the tuple.

        value : tuple
            The tuple itself.


        Returns
        -------
        tuple
            If provided, overwrites the value of the tuple.

        """
        self.log(iid, "Tuple", "items:", items)

    # Operations

    def operation(
        self, dyn_ast: str, iid: int, operator: str, operands: List[Any], result: Any
    ) -> Any:
        """Hook for any operation.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        operator : str
            The operator of the operation.

        operands : List[Any]
            The operands of the operation.

        result : Any
            The result of the operation.


        Returns
        -------
        Any
            If provided, overwrites the result of the operation.

        """
        pass

    def binary_operation(
        self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any
    ) -> Any:
        """Hook for any binary operation.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        op : str
            The operator of the operation.

        left : Any
            The left operand of the operation.

        right : Any
            The right operand of the operation.

        result : Any
            The result of the operation.


        Returns
        -------
        Any
            If provided, overwrites the result of the operation.

        """
        self.log(iid, "Binary Operation", left, op, right, "->", result)

    def add(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def bit_and(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def bit_or(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def bit_xor(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def divide(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def floor_divide(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def left_shift(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def right_shift(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def matrix_multiply(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def modulo(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def multiply(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def power(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def subtract(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def _and(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def _or(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Binary Operation", left, right, "->", result)

    def unary_operation(
        self, dyn_ast: str, iid: int, opr: Any, arg: Any, result: Any
    ) -> Any:
        """Hook for any unary operation.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        opr : str
            The operator of the operation.

        arg : Any
            The operand of the operation.

        result : Any
            The result of the operation.


        Returns
        -------
        Any
            If provided, overwrites the result of the operation.

        """
        self.log(iid, "Unary Operation", arg, "->", result)

    def bit_invert(self, dyn_ast: str, iid: int, arg: Any, result: Any) -> Any:
        self.log(iid, "Unary Operation", arg, "->", result)

    def minus(self, dyn_ast: str, iid: int, arg: Any, result: Any) -> Any:
        self.log(iid, "Unary Operation", arg, "->", result)

    def _not(self, dyn_ast: str, iid: int, arg: Any, result: Any) -> Any:
        self.log(iid, "Unary Operation", arg, "->", result)

    def plus(self, dyn_ast: str, iid: int, arg: Any, result: Any) -> Any:
        self.log(iid, "Unary Operation", arg, "->", result)

    def comparison(
        self, dyn_ast: str, iid: int, op: str, left: Any, right: Any, result: Any
    ) -> Any:
        """Hook for the comparison operation.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        op : str
            The operator of the operation.

        left : Any
            The left operand of the operation.

        right : Any
            The right operand of the operation.

        result : Any
            The result of the operation.


        Returns
        -------
        Any
            If provided, overwrites the result of the operation.

        """
        self.log(iid, "Comparison", left, op, right, "->", result)

    def equal(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def greater_than(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def greater_than_equal(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def _in(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def _is(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def less_than(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def less_than_equal(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def not_equal(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def is_not(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    def not_in(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        self.log(iid, "Comparison", left, right, "->", result)

    # Memory access

    def memory_access(self, dyn_ast: str, iid: int, val: Any) -> Any:
        """Hook for any memory access, currently, except some write operations.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The value accessed.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(iid, "Accessing")

    def read(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, " Reading")

    def read_identifier(self, dyn_ast: str, iid: int, val: Any) -> Any:
        self.log(iid, "    Reading")

    def write(
        self, dyn_ast: str, iid: int, old_vals: List[Callable], new_val: Any
    ) -> Any:
        """Hook for writes.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        old_vals : Any
            A list of old values before the write takes effect.
            It's a list to support multiple assignments.
            Each old value is wrapped into a lambda function, so that
            the analysis writer can decide if and when to evaluate it.

        new_val : Any
            The value after the write takes effect.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(iid, "    Writing")

    def delete(
        self, dyn_ast: str, iid: int, val: List[Tuple[Any, Any, bool]]
    ) -> Optional[bool]:
        """Hook for deletes.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : List[Tuple[Any, Any, bool]]
            The list of values to be deleted. Each item in the list is a tuple of the form
            (base, offset, is_sub). `is_sub` is True if the value is a subscript, e.g. `a[b]`.


        Returns
        -------
        Any
            If True cancels the deletion.

        """
        self.log(iid, "    Deleting")

    def read_attribute(
        self, dyn_ast: str, iid: int, base: Any, name: str, val: Any
    ) -> Any:
        """Hook for reading an object attribute.

        E.g. `obj.attr`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        base : Any
            The object to which the attribute is attached.

        name : str
            The name of the attribute.

        val : Any
            The resulting value.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(iid, "Attribute", name)

    def read_subscript(
        self, dyn_ast: str, iid: int, base: Any, sl: List[Union[int, Tuple]], val: Any
    ) -> Any:
        """Hook for reading a subscript, also known as a slice.

        E.g. `obj[1, 2]`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        base : Any
            The object to which the subscript is attached.

        sl : List[Union[int, Tuple]]
            The subscript.

        val : Any
            The resulting value.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(iid, "Slice", sl)

    # Instrumented function

    def function_enter(
        self, dyn_ast: str, iid: int, args: List[Any], name: str, is_lambda: bool
    ) -> None:
        """Hook for when an instrumented function is entered.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        args : List[Any]
            The arguments passed to the function.

        name:
            Name of the function called.

        is_lambda : bool
            Whether the function is a lambda function.

        """
        tmp = self._get_ast(dyn_ast)
        if tmp is not None:
            ast, iids = tmp
        else:
            return
        if (not is_lambda) and (
            get_node_by_location(ast, iids.iid_to_location[iid], m.FunctionDef()).name
            in ["__str__", "__repr__"]
        ):
            self.log(iid, "Entered function", danger_of_recursion=True)

    def function_exit(
        self, dyn_ast: str, function_iid: int, name: str, result: Any
    ) -> Any:
        """Hook for exiting an instrumented function.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        function_iid: int
            ID unique to the current file, referring to the function.

        name: str
            Name of the function called.

        result : Any
            The result of the function.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(function_iid, "Exiting function")

    def _return(
        self, dyn_ast: str, iid: int, function_iid: int, function_name: str, value: Any
    ) -> Any:
        """Hook for instrumented return statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid: int
            ID unique to the current file, referring to the return statement.

        function_iid: int
            ID unique to the current file, referring to the function.

        function_name: str
            Name of the function returning from.

        value : Any
            The value returned.

        """
        self.log(iid, "   Returning", value)

    def _yield(
        self, dyn_ast: str, iid: int, function_iid: int, function_name: str, value: Any
    ) -> Any:
        """Hook for instrumented yield statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid: int
            ID unique to the current file, referring to the yield statement.

        function_iid: int
            ID unique to the current file, referring to the function.

        function_name: str
            Name of the function yielding from.

        value : Any
            The value yielded.

        """
        self.log(iid, "   Yielding", value)

    def implicit_return(
        self, dyn_ast: str, iid: int, function_iid: int, function_name: str, value: Any
    ) -> Any:
        """Hook for exiting a function without a return or yield (by reaching the end of function body).


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid: int
            ID unique to the current file, referring to the function definition.

        function_iid: int
            ID unique to the current file, referring to the function definition.

        function_name: str
            Name of the function exiting.

        value : Any
            The value returned (None).

        """
        self.log(iid, "   Exiting function")

    # Function Call

    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ):
        """Hook called before a function call happens.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        function : str
            Function which will be called.

        pos_args : Tuple
            The positional arguments passed to the function.

        kw_args : Dict
            The keyword arguments passed to the function.

        """
        self.log(iid, "Before function call")

    def post_call(
        self,
        dyn_ast: str,
        iid: int,
        result: Any,
        call: Callable,
        pos_args: Tuple,
        kw_args: Dict,
    ) -> Any:
        """Hook called after a function call.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        val : Any
            The return value of the function.

        call: Callable
            The function which was called.

        pos_args : Tuple
            The positional arguments passed to the function.

        kw_args : Dict
            The keyword arguments passed to the function.


        Returns
        -------
        Any
            If provided, overwrites the returned value.

        """
        self.log(iid, "After function call")

    # Statements

    def augmented_assignment(
        self, dyn_ast: str, iid: int, left: Any, op: str, right: Any
    ) -> Any:
        """Hook for any augmented assignment.

        E.g. `a += 1`

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        left : Any
            The left operand.

        op : str
            The operator.

        right : Any
            The right operand.

        val : Any
            The resulting value.


        Returns
        -------
        Any
            If provided, overwrites the result.

        """
        self.log(iid, "Augmented assignment", left, op, right)

    def add_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def bit_and_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def bit_or_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def bit_xor_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def divide_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def floor_divide_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def left_shift_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def matrix_multiply_assign(
        self, dyn_ast: str, iid: int, left: Any, right: Any
    ) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def modulo_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def multiply_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def power_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def right_shift_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def subtract_assign(self, dyn_ast: str, iid: int, left: Any, right: Any) -> Any:
        self.log(iid, "Augmented assignment", left, right)

    def _raise(
        self, dyn_ast: str, iid: int, exc: Exception, cause: Any
    ) -> Optional[Exception]:
        """Hook for instrumented raise statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        exc : Exception
            The exception raised.

        cause : Any
            The cause of the exception.


        Returns
        -------
        Exception
            If provided, changes the exception raised.

        """
        self.log(iid, "Exception raised", exc, "because of", cause)

    def _assert(
        self, dyn_ast: str, iid: int, condition: bool, message: str
    ) -> Optional[bool]:
        """Hook for assert statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        condition : bool
            The condition to assert.

        message : str
            The message to display if the condition is false.


        Returns
        -------
        bool
            If provided, changes the condition of assert.

        """
        self.log(iid, "Asserting", condition, "with message", message)

    # Control flow

    def control_flow_event(self, dyn_ast: str, iid: int) -> None:
        """Hook called when a control flow event happens.

        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.
        """
        self.log(iid, "Control flow event")

    def enter_control_flow(
        self, dyn_ast: str, iid: int, cond_value: bool
    ) -> Optional[bool]:
        """Hook called when entering a control flow branch.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        cond_value : bool
            The value of the condition.


        Returns
        -------
        bool
            If provided, changes the condition of the control flow.

        """
        self.log(iid, "Control-flow enter", "with condition", cond_value)

    def exit_control_flow(self, dyn_ast: str, iid: int) -> None:
        """Hook called when exiting a control flow branch.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        """
        self.log(iid, "Control-flow exit")

    def enter_if(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        """Hook called when entering if.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        cond_value : bool
            Whether the condition is true or false.


        Returns
        -------
        Optional[bool]
            If provided, overwrites the condition (which may change the branch outcome).

        """
        self.log(iid, "   If", cond_value)

    def exit_if(self, dyn_ast, iid):
        """Hook for exiting if.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.


        """
        self.log(iid, "If exit")

    def enter_for(
        self, dyn_ast: str, iid: int, next_value: Any, iterable: Iterable
    ) -> Optional[Any]:
        """Hook for entering a single iteration of a for loop.


        In most cases it should be ensured that the provided iterable is not consumed
        as the instrumented program will use it later on in the actual for loop.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        next_value : Any
            The next value of the iterator.

        iterable: Iterable
            Iterable used in the for loop.


        Returns
        -------
        Any
            If provided, overwrites the value of the iterator.

        """
        self.log(iid, "   For", next_value)

    def exit_for(self, dyn_ast, iid):
        """Hook for exiting a for loop.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.


        """
        self.log(iid, "For exit")

    def enter_while(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        """Hook for entering the next iteration of a while loop.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        cond_value : bool
            The value of the condition (which may change the branch outcome).


        Returns
        -------
        bool
            If provided, overwrites the condition.

        """
        self.log(iid, "   While", cond_value)

    def exit_while(self, dyn_ast, iid):
        """Hook for exiting a while loop.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.


        """
        self.log(iid, "While exit")

    def _break(self, dyn_ast: str, iid: int) -> Optional[bool]:
        """Hook for break statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.


        Returns
        -------
        bool
            If False, cancels the break.

        """
        self.log(iid, "Break")

    def _continue(self, dyn_ast: str, iid: int) -> Optional[bool]:
        """Hook for continue statement.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.


        Returns
        -------
        bool
            If False, cancels continue.

        """
        self.log(iid, "Continue")

    def enter_try(self, dyn_ast: str, iid: int) -> None:
        """Hook for entering a try block.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        """
        self.log(iid, "Entered try")

    def clean_exit_try(self, dyn_ast: str, iid: int) -> None:
        """Hook for exiting a try block without an exception being raised.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid: int
            Unique ID of the syntax tree node.
        """
        self.log(iid, "Clean exit try")

    def exception(
        self, dyn_ast: str, iid: int, exceptions: List[Exception], caught: Exception
    ) -> Optional[Exception]:
        """Hook for entering an except block.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        exceptions : List[Exception]
            The exceptions to catch.

        caught : Exception
            The exception caught.


        Returns
        -------
        Exception
            If provided, overwrites the exception caught.

        """
        self.log(iid, "Caught", caught, "from", exceptions)

    # Top level

    def runtime_event(self, dyn_ast: str, iid: int) -> None:
        """Hook for any runtime event.


        Parameters
        ----------
        dyn_ast : str
            The path to the original code. Can be used to extract the syntax tree.

        iid : int
            Unique ID of the syntax tree node.

        """
        pass

    def uncaught_exception(self, exc: Exception, stack_trace: TracebackType) -> None:
        """Hook for any uncaught exceptions.


        Parameters
        ----------
        exc : Exception
            The exception raised.

        stack_trace : TracebackType
            The stack trace of the exception.

        """
        self.log(-1, "Uncaught exception", exc, stack_trace)

    def begin_execution(self) -> None:
        """Hook for the start of execution."""
        self.log(-1, "Execution started")

    def end_execution(self) -> None:
        """Hook for the end of execution."""
        self.log(-1, "Execution ended")
