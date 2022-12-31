from typing import Callable
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location, get_parent_by_type

class CallGraph(BaseAnalysis):
    def __init__(self):
        super(CallGraph, self).__init__()
        self.graph = set()

    def pre_call(self, dyn_ast: str, iid: int, function: Callable):
        ast, iids = self._get_ast(dyn_ast)
        caller = get_parent_by_type(ast, iids.iid_to_location[iid], m.FunctionDef())
        callee = get_node_by_location(ast, iids.iid_to_location[iid], m.Call())
        if caller is None:
            f = 'root module'
        else:
            f = caller.name.value
        if callee is None:
            t = 'unknown'
        else:
            t = callee.func.value
        self.graph.add((f, t))
    
    def end_execution(self):
        print(self.graph)