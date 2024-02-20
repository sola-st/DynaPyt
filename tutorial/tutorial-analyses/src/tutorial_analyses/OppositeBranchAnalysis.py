from typing import Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class OppositeBranchAnalysis(BaseAnalysis):
    def enter_control_flow(
        self, dyn_ast: str, iid: int, cond_value: bool
    ) -> Optional[bool]:
        return not cond_value
