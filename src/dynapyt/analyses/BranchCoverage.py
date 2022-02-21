from typing import Optional
from .BaseAnalysis import BaseAnalysis

class BranchCoverage(BaseAnalysis):
    def __init__(self, iids):
        self.branches = dict()
        self.iids = iids

    def enter_ctrl_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.branches[(iid, cond_value)] = self.branches.get((iid, cond_value), 0) + 1
    
    
    def end_execution(self):
        for k, v in self.branches.items():
            print(f'Branch {k[0]} taken with condition {k[1]}, {v} time{"" if v == 1 else "s"}')