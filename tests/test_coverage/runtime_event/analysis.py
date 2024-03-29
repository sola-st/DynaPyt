from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin_execution")

    def end_execution(self):
        print("end_execution")

    def runtime_event(self, dyn_ast, iid):
        print(f"runtime_event @ {iid}")
