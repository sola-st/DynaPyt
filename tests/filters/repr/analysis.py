from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import ignore


class Analysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    @ignore(patterns=["foo"])
    def pre_call(self, dyn_ast, iid, function, pos_args, kw_args):
        print(f"pre call at {iid}")
