from typing import Any, Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.IIDs import IIDs


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def enter_control_flow(
        self, dyn_ast: str, iid: int, cond_value: bool
    ) -> Optional[bool]:
        print(f"enter control flow event with condition {cond_value}")

    def enter_if(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        print(f"if expression evaluates to {cond_value}")

    def exit_if(self, dyn_ast: str, iid: int):
        print(f"done with if expression")

    def exit_control_flow(self, dyn_ast: str, iid: int) -> None:
        print(f"done with control flow statement")

    def end_execution(self) -> None:
        print("end execution")
