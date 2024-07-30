from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.utils.AnalysisUtils import get_old_value


class TestAnalysis(BaseAnalysis):
    def write(self, dyn_ast: str, iid: int, old_vals: Any, new_val: Any) -> Any:
        old = get_old_value(old_vals[0])
        print(f"write with old={old} and new={new_val}")
        if isinstance(new_val, str):
            return "abc"
