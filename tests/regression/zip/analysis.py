import collections
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    def post_call(self, dyn_ast, iid, result, call, pos_args, kw_args):
        print(f"post call of {call.__name__}")

    def pre_call(self, dyn_ast, iid, function, pos_args, kw_args):
        if isinstance(pos_args[0], collections.abc.Iterator):
            x = list(pos_args[0])
            pos_args[0] = x
