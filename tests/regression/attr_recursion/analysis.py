from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def read_attribute(self, dyn_ast, iid, base, attr, val):
        pass

    def read_identifier(self, dyn_ast, iid, val):
        pass

    def post_call(self, dyn_ast, iid, result, function, pos_args, kw_args):
        if result is function:
            return
        _self = function
        if isinstance(_self, str):
            pass
        print(f"Function call")

    def end_execution(self):
        print("end execution")
