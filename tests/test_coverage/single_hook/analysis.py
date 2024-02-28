from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin_execution")

    def end_execution(self):
        print("end_execution")

    def add(self, dyn_ast, iid, left, right, result):
        print(f"add: {left} + {right} = {result}")
