from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def read_attribute(self, dyn_ast, iid, base, attr, value):
        print(f"Reading attribute {attr} from {base} with value {value}")
