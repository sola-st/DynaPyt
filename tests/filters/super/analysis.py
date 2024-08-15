from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only


class TestAnalysis(BaseAnalysis):
    @only(patterns=["foo"])
    def post_call(self, dyn_ast: str, iid: int, result, call, pos_args, kw_args):
        print(f"post call of {call}")
