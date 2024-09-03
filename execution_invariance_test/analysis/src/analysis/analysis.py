
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class Analysis(BaseAnalysis):

    def runtime_event(self, dyn_ast: str, iid: int) -> None:
        pass