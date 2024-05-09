from .BaseAnalysis import BaseAnalysis
from typing import Any

class LiteralAnalysis(BaseAnalysis):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def literal(self, dyn_ast: str, iid: int, value: Any) -> Any:
        print(str(iid) + ': Literal')
