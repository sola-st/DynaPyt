from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    @only(patterns=["'abc'", '"abc"', "abc"])
    def string(self, dyn_ast: str, iid: int, val: Any) -> Any:
        print(f'string literal "{val}"')

    def end_execution(self) -> None:
        print("end execution")
