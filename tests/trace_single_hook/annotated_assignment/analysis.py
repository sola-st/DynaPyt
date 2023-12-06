from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def read(self, dyn_ast, iid, value):
        print(f"read value {value}")

    def write(self, dyn_ast, iid, old_values, new_value):
        print(f"Writing {new_value} to {[ov.__code__.co_names for ov in old_values]}")

    def end_execution(self) -> None:
        print("end execution")
