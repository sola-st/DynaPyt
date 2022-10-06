from typing import Any, Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs


class TestAnalysis(BaseAnalysis):
    def multiply(self, dyn_ast: str, iid: int, left: Any, right: Any, result: Any) -> Any:
        print(f"multiplying {left} and {right} gives {result}")
