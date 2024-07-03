from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def enter_with(self, dyn_ast: str, iid: int, ctx_manager):
        print(f"with statement entered")

    def exit_with(self, dyn_ast: str, iid: int, is_suppressed: bool, exc_value):
        print(f"with statement exited")
        
    def runtime_event(self, dyn_ast: str, iid: int) -> None:
        print("runtime event")

    def control_flow_event(self, dyn_ast: str, iid: int) -> None:
        print("control flow event")
        
    def end_execution(self) -> None:
        print("end execution")