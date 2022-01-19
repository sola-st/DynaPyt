from typing import Any, List, Optional, Tuple
from .BaseAnalysis import BaseAnalysis

class UnnecessaryDoubleDictQuery(BaseAnalysis):

    # still incomplete

    def binary_op(self, iid: int, op: str, left: Any, right: Any, result: Any) -> Any:
        # TODO: doesn't seem to work on "x in y"
        print(f"{op} {left} {right}")
