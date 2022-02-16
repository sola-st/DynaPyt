import logging
from typing import Optional
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location, get_parent_by_type

class CallGraph(BaseAnalysis):
    def __init__(self, iids):
        self.graph = set()
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


    def pre_call(self, dyn_ast: str, iid: int):
        ast = self.__get_ast(dyn_ast)
        caller = get_parent_by_type(ast, self.iids.iid_to_location[iid], m.FunctionDef())
        callee = get_node_by_location(ast, self.iids.iid_to_location[iid], m.Call())
        if caller is None:
            f = 'root module'
        else:
            f = caller.name.value
        if callee is None:
            t = 'unknown'
        else:
            t = callee.func.value
        self.graph.add((f, t))
        self.__log('From', f, 'calling', t)
    
    def end_execution(self):
        print(self.graph)