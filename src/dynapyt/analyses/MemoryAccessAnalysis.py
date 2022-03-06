import logging
from .BaseAnalysis import BaseAnalysis
from typing import Any

class MemoryAccessAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
        self.danger_of_recursion = False
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def log(self, iid: int, *args):
        res = ''
        for arg in args:
            if self.danger_of_recursion:
                res += ' ' + str(hex(id(arg)))
            else:
                res += ' ' + str(arg)
        logging.info(str(iid) + ': ' + res[:80])
    
    def memory_access(self, dyn_ast: str, iid: int, value: Any) -> Any:
        self.log(iid, 'Accessing memory:', value)
