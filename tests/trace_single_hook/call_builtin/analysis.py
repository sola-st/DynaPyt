from typing import Callable, Dict, Tuple, Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

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
        print("end execution")
