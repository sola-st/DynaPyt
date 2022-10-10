from dynapyt.analyses.BaseAnalysis import BaseAnalysis

class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")
    
    def read(self, dyn_ast, iid, value):
        print(f"read value {value}")

    def end_execution(self) -> None:
        print("end execution")