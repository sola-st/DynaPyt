from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    def comparison(self, dyn_ast, iid, left, op, right, result):
        print(f"Comparing {left} {op} {right} = {result}")
