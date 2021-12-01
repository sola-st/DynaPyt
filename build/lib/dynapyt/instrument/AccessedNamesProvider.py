import libcst as cst


class IsParamProvider(cst.BatchableMetadataProvider[list]):
    """
    Marks Name nodes found as a parameter to a function.
    """
    def __init__(self) -> None:
        super().__init__()
        self.is_param = False

    def visit_Param(self, node: cst.Param) -> None:
        # Mark the child Name node as a parameter
        self.set_metadata(node.name, True)

    def visit_Name(self, node: cst.Name) -> None:
        # Mark all other Name nodes as not parameters
        if not self.get_metadata(type(self), node, False):
            self.set_metadata(node, False)