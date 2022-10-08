from typing import Optional, Any
from .BaseAnalysis import BaseAnalysis
from random import random

class ManipulateExec(BaseAnalysis):
    def enter_if(self, f: str, iid: int, cond_value: bool) -> Optional[bool]:
        if random() < 0.5:
            return not cond_value

    def write(self, f: str, iid: int, old_vals: Any, new_val: Any) -> Any:
        if new_val == 23:
            return 42