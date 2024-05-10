from dynapyt.analyses.BaseAnalysis import BaseAnalysis

class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def enter_try(self, dyn_ast: str, iid: int) -> None:
        print(f"entered try block")

    def clean_exit_try(self, dyn_ast: str, iid: int) -> None:
        print(f"clean exit try block")
        
    def end_execution(self) -> None:
        print("end execution")