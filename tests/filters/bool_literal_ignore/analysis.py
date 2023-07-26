from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import ignore


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    @ignore(patterns=["False"])
    def boolean(self, dyn_ast: str, iid: int, val: Any) -> Any:
        print(f"boolean literal {val}")

    def end_execution(self) -> None:
        print("end execution")
