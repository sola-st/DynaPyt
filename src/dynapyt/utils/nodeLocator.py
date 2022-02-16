from collections import namedtuple
import libcst as cst
import libcst.matchers as m
from libcst.metadata import PositionProvider

def wraps(pos, loc):
    if pos.start.line > loc[0]:
        return False
    elif (pos.start.line == loc[0]) and (pos.start.column > loc[1]):
        return False
    if pos.end.line < loc[2]:
        return False
    elif (pos.end.line == loc[2]) and (pos.end.column < loc[3]):
        return False
    return True

Location = namedtuple("Location", ["file", "start_line", "start_column", "end_line", "end_column"])

class Exact(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, loc, typ=m.BaseMatcherNode()):
        self.result = None
        self.loc = loc
        self.typ = typ
        self.found = False
    
    def on_visit(self, node) -> bool:
        if self.found:
            return False
        pos = self.get_metadata(PositionProvider, node)
        if (pos.start.line, pos.start.column, pos.end.line, pos.end.column) == tuple(self.loc[1:]):
            self.result = node
            if m.matches(node, self.typ):
                self.found = True
                return False
        return True

class Parent(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)
    def __init__(self, loc, typ):
        self.result = None
        self.loc = loc
        self.typ = typ
        self.found = False
    
    def on_visit(self, node) -> bool:
        if self.found:
            return False
        pos = self.get_metadata(PositionProvider, node)
        if m.matches(node, self.typ):
            if wraps(pos, self.loc[1:]):
                self.result = node
        if (pos.start.line, pos.start.column, pos.end.line, pos.end.column) == tuple(self.loc[1:]):
            self.found = True
            return False
        return True

def get_node_by_location(ast: cst.CSTNodeT, location: Location, node_type=m.BaseMatcherNode()) -> cst.CSTNodeT:
    ast_wrapper = cst.metadata.MetadataWrapper(ast)
    exact = Exact(location, node_type)
    _ = ast_wrapper.visit(exact)
    return exact.result

def get_parent_by_type(ast: cst.CSTNodeT, location: Location, node_type) -> cst.CSTNodeT:
    ast_wrapper = cst.metadata.MetadataWrapper(ast)
    parent = Parent(location, node_type)
    _ = ast_wrapper.visit(parent)
    return parent.result