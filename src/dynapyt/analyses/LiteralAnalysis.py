from .BaseAnalysis import BaseAnalysis
from typing import Any

class LiteralAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
    
    def literal(self, dyn_ast: str, iid: int, value: Any) -> Any:
        print(str(iid) + ': Literal')
