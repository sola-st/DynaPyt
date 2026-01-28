from typing import Callable, Dict, Tuple, Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ):
        if function.__name__ == "print":
            print(f"Print at {iid} located at {self.iid_to_location(dyn_ast, iid).start_line}")

    def end_execution(self) -> None:
        print("end execution")
