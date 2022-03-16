from .BaseAnalysis import BaseAnalysis
from typing import Any, List

class OperationAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
    
    def operation(self, dyn_ast: str, iid: int, operator: str, operands: List[Any], result: Any) -> Any:
        print(str(iid) + ': Operation')
