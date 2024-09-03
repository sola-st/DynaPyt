from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def _in(self, dyn_ast, iid, left, right, result):
        print(f"Checking if {left} is in {right} --> {result}")
