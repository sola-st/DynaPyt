from typing import Optional, Iterable
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def enter_control_flow(
        self, dyn_ast: str, iid: int, cond_value: bool
    ) -> Optional[bool]:
        print(f"enter control flow event with condition {cond_value}")

    def enter_for(
        self, dyn_ast: str, iid: int, next_value: bool, iterable: Iterable
    ) -> Optional[bool]:
        print(f"for condition evaluates to {next_value}")

    def exit_for(self, dyn_ast: str, iid: int):
        print(f"done with for statement")

    def exit_control_flow(self, dyn_ast: str, iid: int) -> None:
        print(f"done with control flow statement")

    def end_execution(self) -> None:
        print("end execution")
