from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def write(self, dyn_ast, iid, old_vals, new_val):
        print(f"write value {new_val}")

    def end_execution(self) -> None:
        print("end execution")
