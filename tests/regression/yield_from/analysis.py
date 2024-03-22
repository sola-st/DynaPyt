from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    def write(self, dyn_ast, iid, left, right):
        print(f"Writing {right}")
