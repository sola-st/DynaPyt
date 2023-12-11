from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from typing import Any


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print(f"begin execution")

    def function_exit(
        self, dyn_ast: str, function_iid: int, name: str, result: Any
    ) -> Any:
        print(f"Exiting function {name} with result {result}")

    def end_execution(self) -> None:
        print(f"end execution")
