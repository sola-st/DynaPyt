import logging
from typing import Optional
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location, get_parent_by_type

class BranchCoverage(BaseAnalysis):
    def __init__(self, iids):
        self.branches = dict()
        self.iids = iids
        self.asts = {}
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def __log(self, *args):
        res = ''
        for arg in args:
            res += ' ' + str(arg)
        logging.info(res[:80])
    
    def __get_ast(self, filepath: str) -> cst.CSTNodeT:
        if filepath not in self.asts:
            src = ''
            with open(filepath, 'r') as file:
                src = file.read()
            self.asts[filepath] = cst.parse_module(src)

        return self.asts[filepath]

    def enter_ctrl_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        self.branches[(iid, cond_value)] = self.branches.get((iid, cond_value), 0) + 1
    
    
    def end_execution(self):
        for k, v in self.branches.items():
            print(f'Branch {k[0]} taken with condition {k[1]}, {v} time{"" if v < 2 else "s"}')