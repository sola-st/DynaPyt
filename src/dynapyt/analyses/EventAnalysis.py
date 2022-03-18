from .BaseAnalysis import BaseAnalysis

class EventAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
    
    def runtime_event(self, dyn_ast, iid):
        print('.', end='')