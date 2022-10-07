from typing import Any
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def literal(self, dyn_ast: str, iid: int, val: Any) -> Any:
        print(f"literal hook called: {val}")
        if val == 5:
            return "abc"
