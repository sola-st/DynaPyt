from .BaseAnalysis import BaseAnalysis

class OnlyAddAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
    
    def add(self, dyn_ast, iid, left, opr, right):
        print(str(iid) + ': Add')