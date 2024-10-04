from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def _break(self, dyn_ast, iid, loop_iid):
        print(f"breaking at {iid} of {loop_iid}")

    def _continue(self, dyn_ast, iid, loop_iid):
        print(f"continuing at {iid} of {loop_iid}")
