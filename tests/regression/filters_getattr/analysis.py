from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only


class TestAnalysis(BaseAnalysis):
    @only(patterns=["foo"])
    def pre_call(self, dyn_ast: str, iid: int, function, pos_args, kw_args) -> None:
        print(f"pree call of {function.__name__}")
