import libcst as cst
import os.path as path
from ..instrument.IIDs import IIDs, Location

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
    
    def iid_to_location(self, filepath: str, iid: int) -> Location:
        return IIDs(filepath).iid_to_location[iid]
    
    def location_to_iid(self, filepath: str, location: Location) -> int:
        return IIDs(filepath).location_to_iid[location]