from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    def write(self, dyn_ast, iid, old_values, new_value):
        print(f"Writing {new_value} to {[ov.__code__.co_names for ov in old_values]}")
