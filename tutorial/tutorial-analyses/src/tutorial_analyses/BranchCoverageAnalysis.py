from typing import Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class BranchCoverageAnalysis(BaseAnalysis):
    def __init__(self):
        super().__init__()
        self.branches = {}

    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool):
        if (dyn_ast, iid, cond_value) not in self.branches:
            self.branches[(dyn_ast, iid, cond_value)] = 0
        self.branches[(dyn_ast, iid, cond_value)] += 1

    def end_execution(self):
        for k, v in self.branches.items():
            print(f"Branch {k[1]} was taken with value {k[2]} {v} times")
