from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self):
        print("begin execution")

    def function_exit(self, dyn_ast, iid, name, result):
        print(f"function {name} exited with result {result}")

    def end_execution(self):
        print("end execution")
