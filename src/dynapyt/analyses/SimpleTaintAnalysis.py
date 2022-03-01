import libcst.matchers as m
from .BaseAnalysis import BaseAnalysis
from ..utils.nodeLocator import get_node_by_location
from aiopg.connection import Connection, Cursor
from aiohttp.web import Request

class SimpleTaintAnalysis(BaseAnalysis):
    
    def __init__(self, iids) -> None:
        super().__init__()
        self.tainted = set()
        self.seen_source = False
        self.seen_sink = False
        self.warning = False
        self.iids = iids

    def write(self, dyn_ast, iid, old_val, new_val):
        ast = self._get_ast(dyn_ast)
        node = get_node_by_location(ast, self.iids.iid_to_location[iid], m.Assign())
        if m.matches(node, m.Assign(value=m.Await(expression=m.Call(func=m.Attribute(value=m.Name(value='request'), attr=m.Name(value='post')))))):
            self.tainted.add(id(new_val))

    def attribute(self, dyn_ast, iid, base, name, val):
        if isinstance(base, Cursor) and (name == 'execute'):
            self.seen_sink = True
        else:
            if id(base) in self.tainted:
                self.tainted.add(id(val))
            if id(val) in self.tainted:
                self.tainted.add(id(base))
    
    def subscript(self, dyn_ast, iid, base, sl, val):
        if id(base) in self.tainted:
            self.tainted.add(id(val))
        if id(val) in self.tainted:
            self.tainted.add(id(base))
        for i in sl:
            if id(i) in self.tainted:
                self.tainted.add(id(base))
    
    def binary_op(self, dyn_ast, iid, op, left, right, result):
        if (id(left) in self.tainted) or (id(right) in self.tainted):
            self.tainted.add(id(result))
    
    def dictionary(self, dyn_ast, iid, items, value):
        for k, v in items:
            if id(v) in self.tainted:
                self.tainted.add(id(value))

    def pre_call(self, dyn_ast, iid, pos_args, kw_args):
        if self.seen_sink:
            for a in pos_args:
                print(id(a))
                if id(a) in self.tainted:
                    self.warning = True
                    print('!!!!!!!!!!!!!!! Sink reached from unsafe source')
            for k, v in kw_args.items():
                print(id(v))
                if id(v) in self.tainted:
                    print('!!!!!!!!!!!!!!! Sink reached from unsafe source')
                    self.warning = True
        self.seen_sink = False
    
    def end_execution(self):
        if self.warning:
            print('Warning: unsafe path from source to sink!')
        else:
            print('Safe!')