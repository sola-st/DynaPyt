from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import ignore


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    @ignore(patterns=["1"])
    def integer(self, dyn_ast: str, iid: int, val: Any) -> Any:
        print(f"integer literal {val}")

    def end_execution(self) -> None:
        print("end execution")
