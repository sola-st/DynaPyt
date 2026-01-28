from typing import Callable, Dict, Tuple, Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def _continue(self, dyn_ast: str, iid: int, loop_id: int):
        print(f"continue at {iid} in loop {loop_id}")

    def end_execution(self) -> None:
        print("end execution")
