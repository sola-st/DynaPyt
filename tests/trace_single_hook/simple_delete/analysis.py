from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def delete(self, dyn_ast, iid, value):
        print(f"deleting variable {value[0][1][0]}")

    def end_execution(self) -> None:
        print("end execution")
