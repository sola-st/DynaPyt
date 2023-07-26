from typing import Callable, Tuple, Dict
import logging
import libcst as cst
import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_parent_by_type
import json
from inspect import getmodule

class CallGraph(BaseAnalysis):
    def __init__(self):
        super(CallGraph, self).__init__()
        logging.basicConfig(filename="dynapyt.json", format='%(message)s', level=logging.INFO)
        self.graph = {}

    '''
    DynaPyt hook for pre function call
    '''
    def pre_call(self, dyn_ast: str, iid: int, function: Callable, pos_args: Tuple, kw_args: Dict):
        ast, iids = self._get_ast(dyn_ast)
        module = getmodule(function)
        module = str(module).split(' ')[1] if module is not None else "''"
        # calling function 
        caller = get_parent_by_type(ast, iids.iid_to_location[iid], m.FunctionDef())
        # called function
        if hasattr(function, "__qualname__"):
            '''
            module of the callee is added through the module if present
            '''
            callee = module[1:-1] + '.' + function.__qualname__ if module != "''" else function.__qualname__
        else:
            '''
            this is done to capture functions whose function.__qualname__ is not defined,
            but the string gives an idea as to which function is called.
            Captures MarkDecorator annotations, lambdas object calls, etc 
            '''
            temp = str(function)
            callee = temp
        
        #file name
        key = dyn_ast.replace('.py.orig', '').replace('/','.')
        # format = "file"
        
        if caller is None:
            f = key
        else:
            # if caller is a part of class, find the class name
            caller_parent = get_parent_by_type(ast, iids.iid_to_location[iid], m.ClassDef())
            if caller_parent is None:
                f = key + '.' + caller.name.value
                # format += ".func"
            else:
                f = key + '.' + caller_parent.name.value + '.' + caller.name.value
                # format += ".class.func"

        # if caller already added
        if f in self.graph.keys():
            temp = self.graph[f]
            # filter dupilcate callees
            if callee not in temp:
                temp.append(callee)
                self.graph[f] = temp
        else:
            # self.graph[f] = [format, callee]
            self.graph[f] = [callee]
    
    '''
    DynaPyt hook for end of execution
    '''
    def end_execution(self):
        '''
        to avoid serialization failures in converting dict to json
        '''
        try:
            logging.info(json.dumps(self.graph))
        except Exception:
            logging.info("{")
            for idx, key in enumerate(self.graph):
                values = ["\"{}\"".format(x) for x in self.graph[key]]
                if not idx == (len(self.graph.keys()) - 1):
                    logging.info("\"{}\" : {}, ".format(key, values))
                else:
                    logging.info("\"{}\" : {}".format(key, values))
            logging.info("}")
