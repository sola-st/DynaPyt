from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def _list(self, dyn_ast, iid, value):
        print("List")
