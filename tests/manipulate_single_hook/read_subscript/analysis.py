from typing import Any, List, Union, Tuple
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def read_subscript(self, dyn_ast: str, iid: int, base: Any, sl: List[Union[int, Tuple]], val: Any) -> Any:
        print(f"read from base {base} subscript {sl} gives value {val}")
        if type(val) == int:
            return val + 1
        elif type(val) == list:
            return [x + 1 for x in val]
