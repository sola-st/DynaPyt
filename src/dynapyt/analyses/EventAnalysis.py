from .BaseAnalysis import BaseAnalysis

class EventAnalysis(BaseAnalysis):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def runtime_event(self, dyn_ast, iid):
        print('.', end='')