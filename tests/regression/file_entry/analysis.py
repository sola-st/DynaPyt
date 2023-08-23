from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from typing import Callable, Dict, Tuple


class TestAnalysis(BaseAnalysis):
    def pre_call(
        self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict
    ) -> None:
        print(f"pre call of {function.__name__}")
