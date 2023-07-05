from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.filters import only


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    @only(patterns=["a"])
    def read(self, dyn_ast, iid, value):
        print(f"read value {value}")

    def end_execution(self) -> None:
        print("end execution")
