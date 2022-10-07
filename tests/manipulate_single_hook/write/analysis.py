from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def write(self, dyn_ast: str, iid: int, old_val: Any, new_val: Any) -> Any:
        print(f"write with old={old_val} and new={new_val}")
        if type(new_val) == str:
            return "abc"
