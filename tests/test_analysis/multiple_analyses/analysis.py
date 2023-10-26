from typing import Callable, Dict, Tuple, Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestCallAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution of call analysis")

    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        print(f"pre call of {function.__name__}")

    def post_call(
        self,
        dyn_ast: str,
        iid: int,
        result: Any,
        call: Callable,
        pos_args: Tuple,
        kw_args: Dict,
    ) -> Any:
        print(f"post call of {call.__name__}")

    def end_execution(self) -> None:
        print("end execution of call analysis")


class TestIntAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution of int analysis")

    def integer(self, dyn_ast: str, iid: int, val: Any) -> Any:
        print(f"integer literal {val}")

    def end_execution(self) -> None:
        print("end execution of int analysis")


class TestAnalysis(BaseAnalysis):
    def multiply(
        self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any
    ) -> Any:
        print(f"multiplying {left} and {right} gives {result}")
