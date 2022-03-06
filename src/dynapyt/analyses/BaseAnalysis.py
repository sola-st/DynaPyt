import libcst as cst
import os.path as path
from ..instrument.IIDs import IIDs

class BaseAnalysis:

    def __init__(self) -> None:
        self.asts = {}
    
    def _get_ast(self, filepath: str) -> cst.CSTNodeT:
        if not path.exists(filepath):
            return None
        if filepath not in self.asts:
            src = ''
            with open(filepath, 'r') as file:
                src = file.read()
            iids = IIDs(filepath)
            self.asts[filepath] = (cst.parse_module(src), iids)

        return self.asts[filepath]