from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def read_subscript(self, dyn_ast, iid, base, sl, value):
        print(f"read {value}")
