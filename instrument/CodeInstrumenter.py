import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider


class CodeInstrumenter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider,)

    def __init__(self, file_path, iids):
        self.file_path = file_path
        self.iids = iids

    def __create_iid(self, node):
        location = self.get_metadata(PositionProvider, node)
        line = location.start.line
        column = location.start.column
        iid = self.iids.new(self.file_path, line, column)
        return iid

    def __create_import(self, name):
        module_name = cst.Attribute(value=cst.Name(value="brian"), attr=cst.Name(value="runtime"))
        fct_name = cst.Name(value=name)
        imp_alias = cst.ImportAlias(name=fct_name)
        imp = cst.ImportFrom(module=module_name, names=[imp_alias])
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt

    # add import of our runtime library to the file
    def leave_Module(self, node, updated_node):
        new_body = []+list(updated_node.body)
        return updated_node.with_changes(body=new_body)
