from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def add_assign(self, dyn_ast, iid, left, right):
        print(f"add assign: {left} += {right}")
