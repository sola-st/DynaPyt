from dynapyt.analyses.BaseAnalysis import BaseAnalysis

class TestAnalysis(BaseAnalysis):
    def post_call(self, dyn_ast, iid, result, call, pos_args, kw_args):
        print(f"Called with {result}")