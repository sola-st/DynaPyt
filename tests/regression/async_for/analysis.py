from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def enter_for(self, dyn_ast, iid, next_val, iterable):
        print(f"looping {next_val}")
