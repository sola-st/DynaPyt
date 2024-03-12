from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def end_execution(self):
        print("end execution")

    def pre_call(self, dyn_ast, iid, call, pos_args, kw_args):
        print(
            f"pre call of {call.__name__} with pos args {pos_args} and kw args {kw_args}"
        )
