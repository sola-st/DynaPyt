from typing import Optional
from .BaseAnalysis import BaseAnalysis

class Demo(BaseAnalysis):
    def __init__(self):
        self.branches = dict()

    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.branches[(iid, bool(cond_value))] = self.branches.get((iid, bool(cond_value)), 0) + 1
        return False
    
    def end_execution(self):
        for k, v in self.branches.items():
            print(f'Branch {k[0]} taken with condition {k[1]}, {v} time{"" if v == 1 else "s"}')
