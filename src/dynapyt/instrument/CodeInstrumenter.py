import re
import libcst as cst
from libcst.metadata import (
    ParentNodeProvider,
    PositionProvider,
    ScopeProvider,
    ExpressionContextProvider,
    QualifiedNameProvider,
)
import libcst.matchers as m
from libcst._types import CSTNodeT
from libcst.matchers import call_if_not_inside, call_if_inside
from libcst.metadata.expression_context_provider import ExpressionContext
from libcst.metadata.scope_provider import QualifiedNameSource, ClassScope
from ..utils.hooks import snake
from .IIDs import IIDs
from pathlib import Path


class CodeInstrumenter(m.MatcherDecoratableTransformer):
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        PositionProvider,
        ScopeProvider,
        ExpressionContextProvider,
        QualifiedNameProvider,
    )

    # Internal
    def __init__(self, src, file_path, iids: IIDs, selected_hooks):
        super().__init__()
        self.source = src
        self.file_path = str(Path(file_path).resolve())
        self.iids = iids
        self.name_stack = []
        self.current_try = []
        self.current_class = []
        self.current_function = []
        self.selected_hooks = {
            hook: {
                "only": [re.compile(p) for p in details["only"]]
                if "only" in details
                else [],
                "ignore": [re.compile(p) for p in details["ignore"]]
                if "ignore" in details
                else [],
            }
            for hook, details in selected_hooks.items()
        }
        self.to_import = set()

        # Blacklisted attributes are appended to the end of the source code.
        # Some programs depend on being able to parse these attributes so
        # there should be an uninstrumented version in the file (e.g. the
        # __version__ attribute may be parsed for the project's version upon
        # installation).
        self.blacklist_names = {
            "__file__",
            "__name__",
            "__doc__",
            "__package__",
            "__class__",
            "__module__",
            "__builtins__",
            "__loader__",
            "__spec__",
            "__cached__",
            "__annotations__",
            "__all__",
            "__path__",
            "__docformat__",
            "__version__",
            "__author__",
            "__email__",
            "__license__",
        }
        self.blacklist_name_objs = [m.Name(name) for name in self.blacklist_names]

        # Blacklisted nodes to append to the end of the file
        self.blacklist_nodes = [cst.Newline(value="\n")]

    def __selected_by_decorators(self, hook: str, node: CSTNodeT) -> bool:
        if not hasattr(node, "value"):
            return False

        node_val: str = node.value
        try:
            if (
                "only" in self.selected_hooks[hook]
                and len(self.selected_hooks[hook]["only"]) > 0
            ):
                for p in self.selected_hooks[hook]["only"]:
                    if p.match(node_val):
                        return True
                return False
            elif (
                "ignore" in self.selected_hooks[hook]
                and len(self.selected_hooks[hook]["ignore"]) > 0
            ):
                for p in self.selected_hooks[hook]["ignore"]:
                    if p.match(node_val):
                        return False
                return True
            else:
                return True
        except:
            return True

    def __create_iid(self, node):
        location = self.get_metadata(PositionProvider, node)
        start_line = location.start.line
        start_column = location.start.column
        end_line = location.end.line
        end_column = location.end.column
        iid = self.iids.new(
            self.file_path + ".orig", start_line, start_column, end_line, end_column
        )
        return iid

    def __create_import(self, names):
        module_name = cst.Attribute(
            value=cst.Name(value="dynapyt"), attr=cst.Name(value="runtime")
        )
        # imp_aliases = [cst.ImportAlias(name=cst.Name(value=name)) for name in names]
        # imp = cst.ImportFrom(module=module_name, names=imp_aliases)
        imp = cst.Import(
            names=[
                cst.ImportAlias(
                    name=module_name, asname=cst.AsName(cst.Name(value="_rt"))
                )
            ]
        )
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt

    def __wrap_in_lambda(self, original_node, updated_node):
        if len(m.findall(original_node, m.Await())) > 0:
            return updated_node
        if m.matches(updated_node, m.Call(func=m.Name("super"), args=[])):
            class_arg = cst.Arg(value=cst.Name(value=self.current_class[-1]))
            function_arg = cst.Arg(
                value=cst.Name(value=self.current_function[-1]["params"].value)
            )
            new_node = updated_node.with_changes(args=[class_arg, function_arg])
            return cst.Lambda(params=cst.Parameters(params=[]), body=new_node)
        used_names = list(m.findall(original_node, m.Name()))
        unique_names = set()
        parameters = []
        try:
            my_scope = self.get_metadata(ScopeProvider, original_node)
        except KeyError:
            my_scope = None
        if isinstance(my_scope, ClassScope):
            for n in used_names:
                try:
                    name_source = self.get_metadata(QualifiedNameProvider, n)
                    n_scope = self.get_metadata(ScopeProvider, n)
                except KeyError:
                    name_source = []
                    n_scope = None
                if (
                    (n.value not in unique_names)
                    and (my_scope == n_scope)
                    and (len(list(name_source)) > 0)
                    and (list(name_source)[0].source == QualifiedNameSource.LOCAL)
                ):
                    parameters.append(
                        cst.Param(
                            name=cst.Name(value=n.value),
                            default=cst.Name(value=n.value),
                        )
                    )
                    unique_names.add(n.value)
        if m.matches(updated_node, m.Tuple()) and (len(updated_node.lpar) == 0):
            lambda_expr = cst.Lambda(
                params=cst.Parameters(params=parameters),
                body=updated_node.with_changes(
                    lpar=[cst.LeftParen()], rpar=[cst.RightParen()]
                ),
            )
        else:
            lambda_expr = cst.Lambda(
                params=cst.Parameters(params=parameters), body=updated_node
            )
        return lambda_expr

    def __as_string(self, s):
        if "\\" in s:
            raw = "r"
        else:
            raw = ""
        if hasattr(self, "quote") and self.quote == '"':
            return raw + "'" + s + "'"
        else:
            return raw + '"' + s + '"'

    def visit_Annotation(self, node):
        return False

    def visit_Decorator(self, node):
        return False

    def visit_AsName(self, node):
        return False

    # Top level

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module):
        imports_index = -1
        abs_path = Path(self.file_path).resolve()
        parse_to_ast = cst.BinaryOperation(
            left=cst.SimpleString(value=self.__as_string(str(abs_path))),
            operator=cst.Add(),
            right=cst.SimpleString('".orig"'),
        )
        get_ast = cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(cst.Name("_dynapyt_ast_"))],
                    value=parse_to_ast,
                )
            ]
        )
        dynapyt_imports = [cst.Newline(value="\n")]
        import_names = list(self.to_import)
        for i in range(len(updated_node.body)):
            if m.matches(updated_node.body[i], m.SimpleStatementLine()) and (
                m.matches(
                    updated_node.body[i].body[0],
                    m.ImportFrom(module=m.Name(value="__future__")),
                )
            ):
                # makes sure that future imports are outside the try / catch block
                imports_index = i

        if len(import_names) > 0:
            dynapyt_imports.append(self.__create_import(import_names))
            dynapyt_imports.append(cst.Newline(value="\n"))
        code_body = list(updated_node.body[imports_index + 1 :])
        handler_call = cst.Call(
            func=cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_catch_")
            ),
            args=[cst.Arg(cst.Name("_dynapyt_exception_"))],
        )
        handler_body = cst.IndentedBlock(
            body=[cst.SimpleStatementLine(body=[cst.Expr(value=handler_call)])]
        )
        try_body = cst.Try(
            body=cst.IndentedBlock(body=code_body),
            handlers=[
                cst.ExceptHandler(
                    body=handler_body,
                    type=cst.Name(value="Exception"),
                    name=cst.AsName(cst.Name(value="_dynapyt_exception_")),
                )
            ],
        )
        new_body = (
            list(updated_node.body[: imports_index + 1])
            + dynapyt_imports
            + [get_ast]
            + [try_body]
            + self.blacklist_nodes
        )
        return updated_node.with_changes(body=new_body)

    def visit_ClassDef(self, node):
        self.current_class.append(node.name.value)

    def leave_ClassDef(self, original_node, updated_node):
        self.current_class.pop()
        return updated_node

    def leave_SimpleStatementSuite(self, original_node, updated_node):
        new_node = cst.IndentedBlock(
            body=[cst.SimpleStatementLine(body=updated_node.body)]
        )
        return new_node

    # Lowest level
    @call_if_not_inside(m.AssignTarget() | m.Import() | m.ImportFrom() | m.Annotation())
    def leave_Name(self, original_node, updated_node):
        if updated_node.value in self.blacklist_names:
            return updated_node
        if (
            ("boolean" in self.selected_hooks)
            and (updated_node.value in ["True", "False"])
            and (self.__selected_by_decorators("boolean", original_node))
        ):
            callee_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_bool_")
            )
            self.to_import.add("_bool_")
            iid = self.__create_iid(original_node)
            ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            val_arg = cst.Arg(value=updated_node)
            call = cst.Call(
                func=callee_name,
                args=[ast_arg, iid_arg, val_arg],
                lpar=original_node.lpar,
                rpar=original_node.rpar,
            )
            return call

        if (
            "read_identifier" not in self.selected_hooks
        ) or not self.__selected_by_decorators("read_identifier", original_node):
            return updated_node
        try:
            context = self.get_metadata(ExpressionContextProvider, original_node)
            name_source = self.get_metadata(QualifiedNameProvider, original_node)
        except KeyError:
            context = -1
            name_source = []
        if len(list(name_source)) == 0:
            return updated_node
        if (context == ExpressionContext.LOAD) and (
            list(name_source)[0].source == QualifiedNameSource.LOCAL
        ):
            callee_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_read_")
            )
            self.to_import.add("_read_")
            iid = self.__create_iid(original_node)
            ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            var_arg = cst.Arg(value=self.__wrap_in_lambda(original_node, updated_node))
            call = cst.Call(
                func=callee_name,
                args=[ast_arg, iid_arg, var_arg],
                lpar=original_node.lpar,
                rpar=original_node.rpar,
            )
            return call
        else:
            return updated_node

    def leave_Integer(self, original_node, updated_node):
        if ("integer" not in self.selected_hooks) or not self.__selected_by_decorators(
            "integer", original_node
        ):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_int_")
        )
        self.to_import.add("_int_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_Float(self, original_node, updated_node):
        if ("_float" not in self.selected_hooks) or not self.__selected_by_decorators(
            "float", original_node
        ):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_float_")
        )
        self.to_import.add("_float_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_Imaginary(self, original_node, updated_node):
        if (
            "imaginary" not in self.selected_hooks
        ) or not self.__selected_by_decorators("imaginary", original_node):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_img_")
        )
        self.to_import.add("_img_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def visit_ConcatenatedString(self, node):
        return False

    def leave_ConcatenatedString(self, original_node, updated_node):
        if ("string" not in self.selected_hooks) or not self.__selected_by_decorators(
            "string", original_node
        ):
            return updated_node

        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_str_")
        )
        self.to_import.add("_str_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )

        return call

    @call_if_not_inside(m.FormattedStringExpression() | m.ConcatenatedString())
    def visit_FormattedString(self, node):
        self.quote = node.end
        return True

    @call_if_not_inside(m.FormattedStringExpression() | m.ConcatenatedString())
    def leave_FormattedString(self, original_node, updated_node):
        self.quote = ""
        if ("string" not in self.selected_hooks) or not self.__selected_by_decorators(
            "string", original_node
        ):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_str_")
        )
        self.to_import.add("_str_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    @call_if_not_inside(m.ConcatenatedString())
    @call_if_inside(m.Assign() | m.AugAssign() | m.Arg() | m.BinaryOperation())
    def leave_SimpleString(self, original_node, updated_node):
        if ("string" not in self.selected_hooks) or not self.__selected_by_decorators(
            "string", original_node
        ):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_str_")
        )
        self.to_import.add("_str_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    @call_if_not_inside(m.AssignTarget() | m.AnnAssign())
    def leave_Dict(self, original_node, updated_node):
        if "dictionary" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_dict_")
        )
        self.to_import.add("_dict_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        elements_arg = []
        for e in updated_node.elements:
            if m.matches(e, m.StarredDictElement()):
                elements_arg.append(cst.Element(e.value))
            else:
                elements_arg.append(
                    cst.Element(
                        value=cst.Tuple(
                            elements=[
                                cst.Element(value=e.key),
                                cst.Element(value=e.value),
                            ]
                        )
                    )
                )
        val_arg = cst.Arg(value=cst.List(elements=elements_arg))
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_DictComp(self, original_node, updated_node):
        if "dictionary" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_dict_")
        )
        self.to_import.add("_dict_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        elements_arg = cst.Element(
            value=cst.Tuple(
                elements=[
                    cst.Element(value=updated_node.key),
                    cst.Element(value=updated_node.value),
                ]
            )
        )
        val_arg = cst.Arg(
            value=cst.ListComp(elt=elements_arg, for_in=updated_node.for_in)
        )
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    @call_if_not_inside(m.AssignTarget() | m.AnnAssign())
    def leave_List(self, original_node, updated_node):
        if "_list" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_list_")
        )
        self.to_import.add("_list_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        elements_arg = updated_node.elements
        val_arg = cst.Arg(value=cst.List(elements=elements_arg))
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_ListComp(self, original_node, updated_node):
        if "list" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_list_")
        )
        self.to_import.add("_list_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    @call_if_not_inside(m.AssignTarget() | m.AnnAssign())
    def leave_Tuple(self, original_node, updated_node):
        if "_tuple" not in self.selected_hooks:
            if len(updated_node.lpar) == 0:
                return updated_node.with_changes(
                    lpar=[cst.LeftParen()], rpar=[cst.RightParen()]
                )
            return updated_node
        par = self.get_metadata(ParentNodeProvider, original_node)
        if m.matches(par, m.CompFor()) and (par.target is original_node):
            return original_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_tuple_")
        )
        self.to_import.add("_tuple_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        elements_arg = [cst.Element(e.value) for e in updated_node.elements]
        val_arg = cst.Arg(value=cst.List(elements=elements_arg))
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, val_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    # Memory access

    def leave_Del(self, original_node, updated_node):
        if ("delete" not in self.selected_hooks) and original_node.deep_equals(
            updated_node
        ):
            return updated_node
        else:
            if "delete" not in self.selected_hooks:
                analyze_arg = cst.Arg(value=cst.Name(value="False"))
            else:
                analyze_arg = cst.Arg(value=cst.Name(value="True"))
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_delete_")
        )
        self.to_import.add("_delete_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        targets = []
        if m.matches(original_node.target, m.Tuple()):
            org_targets = [e.value for e in original_node.target.elements]
            if m.matches(updated_node.target, m.Call()):
                all_targets = [
                    e.value for e in updated_node.target.args[2].value.elements
                ]
            else:
                all_targets = [e.value for e in updated_node.target.elements]
        else:
            all_targets = [updated_node.target]
            org_targets = [original_node.target]
        for t, t_o in zip(all_targets, org_targets):
            if m.matches(t_o, m.Subscript()):
                if m.matches(t, m.Call()):
                    # triplets of (base, offset, is_subscript)
                    targets.append(
                        cst.Element(
                            value=cst.Tuple(
                                elements=[
                                    cst.Element(value=t.args[2].value),
                                    cst.Element(value=t.args[3].value),
                                    cst.Element(value=cst.Name("True")),
                                ]
                            )
                        )
                    )
                else:
                    name_arg = t.value
                    slices = []
                    for i in t.slice:
                        if m.matches(i.slice, m.Slice()):
                            slices.append(
                                cst.Element(
                                    cst.Call(
                                        func=cst.Name("slice"),
                                        args=[
                                            cst.Arg(
                                                i.slice.lower
                                                if i.slice.lower != None
                                                else cst.Name("None")
                                            ),
                                            cst.Arg(
                                                i.slice.upper
                                                if i.slice.upper != None
                                                else cst.Name("None")
                                            ),
                                            cst.Arg(
                                                i.slice.step
                                                if i.slice.step != None
                                                else cst.Name("None")
                                            ),
                                        ],
                                    )
                                )
                            )
                        else:
                            slices.append(cst.Element(i.slice.value))
                    slice_arg = cst.List(elements=slices)
                    targets.append(
                        cst.Element(
                            value=cst.Tuple(
                                elements=[
                                    cst.Element(value=name_arg),
                                    cst.Element(value=slice_arg),
                                    cst.Element(value=cst.Name("True")),
                                ]
                            )
                        )
                    )
            elif m.matches(t_o, m.Attribute()):
                if m.matches(t, m.Call()):
                    targets.append(
                        cst.Element(
                            value=cst.Tuple(
                                elements=[
                                    cst.Element(value=t.args[2].value),
                                    cst.Element(value=t.args[3].value),
                                    cst.Element(value=cst.Name("False")),
                                ]
                            )
                        )
                    )
                else:
                    base_arg = t.value
                    attr_arg = cst.SimpleString(
                        value=self.__as_string(str(t.attr.value))
                    )
                    targets.append(
                        cst.Element(
                            value=cst.Tuple(
                                elements=[
                                    cst.Element(value=base_arg),
                                    cst.Element(value=attr_arg),
                                    cst.Element(value=cst.Name("False")),
                                ]
                            )
                        )
                    )
            elif m.matches(t_o, m.Name()):
                condition = cst.Comparison(
                    left=cst.SimpleString(value='"' + t_o.value + '"'),
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.In(),
                            comparator=cst.Call(func=cst.Name("locals")),
                        )
                    ],
                )
                base = cst.IfExp(
                    test=condition,
                    body=cst.Call(func=cst.Name("locals")),
                    orelse=cst.Call(func=cst.Name("globals")),
                )
                targets.append(
                    cst.Element(
                        value=cst.Tuple(
                            elements=[
                                cst.Element(value=base),
                                cst.Element(
                                    value=cst.List(
                                        elements=[
                                            cst.Element(
                                                value=cst.SimpleString(
                                                    value='"' + t_o.value + '"'
                                                )
                                            )
                                        ]
                                    )
                                ),
                                cst.Element(value=cst.Name("True")),
                            ]
                        )
                    )
                )
        target_arg = cst.Arg(cst.List(elements=targets))
        call = cst.Call(
            func=callee_name, args=[ast_arg, iid_arg, target_arg, analyze_arg]
        )
        return cst.Expr(value=call)

    @call_if_not_inside(m.AssignTarget() | m.AnnAssign())
    def leave_Subscript(self, original_node, updated_node):
        if "read_subscript" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_sub_")
        )
        self.to_import.add("_sub_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        name_arg = cst.Arg(updated_node.value)
        slices = []
        for i in updated_node.slice:
            if m.matches(i.slice, m.Slice()):
                slices.append(
                    cst.Element(
                        cst.Call(
                            func=cst.Name("slice"),
                            args=[
                                cst.Arg(
                                    i.slice.lower
                                    if i.slice.lower != None
                                    else cst.Name("None")
                                ),
                                cst.Arg(
                                    i.slice.upper
                                    if i.slice.upper != None
                                    else cst.Name("None")
                                ),
                                cst.Arg(
                                    i.slice.step
                                    if i.slice.step != None
                                    else cst.Name("None")
                                ),
                            ],
                        )
                    )
                )
            else:
                slices.append(cst.Element(i.slice.value))
        slice_arg = cst.Arg(cst.List(elements=slices))
        return cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, name_arg, slice_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )

    @call_if_not_inside(m.AssignTarget() | m.Import() | m.ImportFrom() | m.Annotation())
    def leave_Attribute(self, original_node, updated_node):
        if "read_attribute" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_attr_")
        )
        self.to_import.add("_attr_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        base_arg = cst.Arg(updated_node.value)
        attr_arg = cst.Arg(
            cst.SimpleString(value=self.__as_string(str(updated_node.attr.value)))
        )
        return cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, base_arg, attr_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )

    # Operations
    def leave_BinaryOperation(self, original_node, updated_node):
        hook_name = snake(type(original_node.operator).__name__)
        if hook_name not in self.selected_hooks:
            return updated_node
        bin_op = {
            "Add": 0,
            "BitAnd": 1,
            "BitOr": 2,
            "BitXor": 3,
            "Divide": 4,
            "FloorDivide": 5,
            "LeftShift": 6,
            "MatrixMultiply": 7,
            "Modulo": 8,
            "Multiply": 9,
            "Power": 10,
            "RightShift": 11,
            "Subtract": 12,
        }
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_binary_op_")
        )
        self.to_import.add("_binary_op_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(self.__wrap_in_lambda(original_node.left, updated_node.left))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bin_op[operator_name])))
        right_arg = cst.Arg(
            self.__wrap_in_lambda(original_node.right, updated_node.right)
        )
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, left_arg, operator_arg, right_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_BooleanOperation(self, original_node, updated_node):
        operator_name = snake(type(original_node.operator).__name__)
        if (
            operator_name not in self.selected_hooks
            and f"_{operator_name}" not in self.selected_hooks
        ):
            return updated_node
        bool_op = {"And": 13, "Or": 14}
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_binary_op_")
        )
        self.to_import.add("_binary_op_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(self.__wrap_in_lambda(original_node.left, updated_node.left))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bool_op[operator_name])))
        right_arg = cst.Arg(
            self.__wrap_in_lambda(original_node.right, updated_node.right)
        )
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, left_arg, operator_arg, right_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_UnaryOperation(self, original_node, updated_node):
        operator_name = snake(type(original_node.operator).__name__)
        if (
            operator_name not in self.selected_hooks
            and f"_{operator_name}" not in self.selected_hooks
        ):
            return updated_node
        un_op = {"BitInvert": 0, "Minus": 1, "Not": 2, "Plus": 3}
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_unary_op_")
        )
        self.to_import.add("_unary_op_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(un_op[operator_name])))
        right_arg = cst.Arg(updated_node.expression)
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, operator_arg, right_arg],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_Comparison(self, original_node, updated_node):
        if not any(
            snake(type(i.operator).__name__) in self.selected_hooks
            for i in updated_node.comparisons
        ):
            return updated_node
        comp_op = {
            "Equal": 0,
            "GreaterThan": 1,
            "GreaterThanEqual": 2,
            "In": 3,
            "Is": 4,
            "LessThan": 5,
            "LessThanEqual": 6,
            "NotEqual": 7,
            "IsNot": 8,
            "NotIn": 9,
        }
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_comp_op_")
        )
        self.to_import.add("_comp_op_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        comparisons = []
        for i in updated_node.comparisons:
            operator_name = type(i.operator).__name__
            comparisons.append(
                cst.Element(
                    value=cst.Tuple(
                        elements=[
                            cst.Element(cst.Integer(str(comp_op[operator_name]))),
                            cst.Element(i.comparator),
                        ]
                    )
                )
            )
        call = cst.Call(
            func=callee_name,
            args=[ast_arg, iid_arg, left_arg, cst.Arg(cst.List(elements=comparisons))],
            lpar=original_node.lpar,
            rpar=original_node.rpar,
        )
        return call

    def leave_Assign(self, original_node, updated_node):
        # Keep track of nodes of blacklisted attributes
        if self.file_path.endswith("__init__.py") and m.matches(
            original_node,
            m.Assign(
                targets=[
                    m.AtLeastN(
                        n=1,
                        matcher=m.AssignTarget(
                            target=m.OneOf(*self.blacklist_name_objs)
                        ),
                    )
                ]
            ),
        ):
            self.blacklist_nodes.append(cst.SimpleStatementLine(body=[original_node]))
            self.blacklist_nodes.append(cst.Newline(value="\n"))
        if "write" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_write_")
        )
        self.to_import.add("_write_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if m.matches(updated_node.value, m.Yield()):
            val_arg = cst.Arg(value=updated_node.value.value)
        else:
            val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(
            value=cst.List(
                elements=[
                    cst.Element(self.__wrap_in_lambda(tu.target, tu.target))
                    for to, tu in zip(original_node.targets, updated_node.targets)
                ]
            )
        )
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg, left_arg])
        if m.matches(updated_node.value, m.Yield()):
            return updated_node.with_changes(
                value=updated_node.value.with_changes(value=call)
            )
        else:
            return updated_node.with_changes(value=call)

    def leave_AnnAssign(self, original_node, updated_node):
        # Keep track of nodes of blacklisted attributes
        if self.file_path.endswith("__init__.py") and m.matches(
            original_node, m.AnnAssign(target=m.OneOf(*self.blacklist_name_objs))
        ):
            self.blacklist_nodes.append(cst.SimpleStatementLine(body=[original_node]))
            self.blacklist_nodes.append(cst.Newline(value="\n"))
        if "write" not in self.selected_hooks or original_node.value is None:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_write_")
        )
        self.to_import.add("_write_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if m.matches(updated_node.value, m.Yield()):
            val_arg = cst.Arg(value=updated_node.value.value)
        else:
            val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(
            value=cst.List(
                elements=[
                    cst.Element(
                        self.__wrap_in_lambda(original_node.target, updated_node.target)
                    )
                ]
            )
        )
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg, left_arg])
        if m.matches(updated_node.value, m.Yield()):
            return updated_node.with_changes(
                value=updated_node.value.with_changes(value=call)
            )
        else:
            return updated_node.with_changes(value=call)

    def leave_AugAssign(self, original_node, updated_node):
        if ("write" not in self.selected_hooks) and (
            snake(type(original_node.operator).__name__) not in self.selected_hooks
        ):
            return updated_node
        aug_op = {
            "AddAssign": 0,
            "BitAndAssign": 1,
            "BitOrAssign": 2,
            "BitXorAssign": 3,
            "DivideAssign": 4,
            "FloorDivideAssign": 5,
            "LeftShiftAssign": 6,
            "MatrixMultiplyAssign": 7,
            "ModuloAssign": 8,
            "MultiplyAssign": 9,
            "PowerAssign": 10,
            "RightShiftAssign": 11,
            "SubtractAssign": 12,
        }
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_aug_assign_")
        )
        self.to_import.add("_aug_assign_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        opr_arg = cst.Arg(value=cst.Integer(value=str(aug_op[operator_name])))
        val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(
            value=self.__wrap_in_lambda(original_node.target, updated_node.target)
        )
        call = cst.Call(
            func=callee_name, args=[ast_arg, iid_arg, left_arg, opr_arg, val_arg]
        )
        return updated_node.with_changes(value=call, target=original_node.target)

    # Function
    def visit_FunctionDef(self, node: cst.FunctionDef):
        iid = self.__create_iid(node)
        params = None
        if len(node.params.params) > 0:
            params = node.params.params[0].name
        elif len(node.params.posonly_params) > 0:
            params = node.params.posonly_params[0].name
        self.current_function.append({"params": params, "name": node.name, "iid": iid})

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        function_metadata = self.current_function.pop()
        if (
            "function_enter" not in self.selected_hooks
            and "implicit_return" not in self.selected_hooks
        ) or not (
            self.__selected_by_decorators("function_enter", function_metadata["name"])
            or self.__selected_by_decorators(
                "implicit_return", function_metadata["name"]
            )
        ):
            return updated_node
        enter_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_func_entry_")
        )
        self.to_import.add("_func_entry_")
        exit_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_func_exit_")
        )
        self.to_import.add("_func_exit_")
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(function_metadata["iid"])))
        name_arg = cst.Arg(
            value=cst.SimpleString(
                value=self.__as_string(function_metadata["name"].value)
            )
        )
        args_arg = cst.Arg(
            value=cst.List(
                elements=[
                    cst.Element(value=self.__wrap_in_lambda(po.name, pu.name))
                    for po, pu in zip(
                        original_node.params.params, updated_node.params.params
                    )
                ]
            )
        )
        entry_stmt = cst.Expr(
            cst.Call(func=enter_name, args=[ast_arg, iid_arg, args_arg, name_arg])
        )
        exit_stmt = cst.Expr(
            cst.Call(func=exit_name, args=[ast_arg, iid_arg, name_arg])
        )
        if m.matches(
            updated_node.body.body[0],
            m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())]),
        ):
            new_body = updated_node.body.with_changes(
                body=[updated_node.body.body[0], cst.SimpleStatementLine([entry_stmt])]
                + list(updated_node.body.body[1:])
                + [cst.SimpleStatementLine([exit_stmt])]
            )
        else:
            new_body = updated_node.body.with_changes(
                body=[cst.SimpleStatementLine([entry_stmt])]
                + list(updated_node.body.body)
                + [cst.SimpleStatementLine([exit_stmt])]
            )
        new_node = updated_node
        return new_node.with_changes(body=new_body)

    def leave_Lambda(self, original_node, updated_node):
        if "lambda" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_lambda_")
        )
        self.to_import.add("_lambda_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        args_arg = cst.Arg(
            value=cst.List(
                elements=[
                    cst.Element(value=self.__wrap_in_lambda(po.name, pu.name))
                    for po, pu in zip(
                        original_node.params.params, updated_node.params.params
                    )
                ]
            )
        )
        body_arg = cst.Arg(
            value=self.__wrap_in_lambda(original_node.body, updated_node.body)
        )
        new_stmt = cst.Call(
            func=callee_name, args=[ast_arg, iid_arg, args_arg, body_arg]
        )
        return updated_node.with_changes(body=new_stmt)

    def leave_Return(self, original_node, updated_node):
        if "_return" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_return_")
        )
        self.to_import.add("_return_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        function_metadata = self.current_function[-1]
        function_iid_arg = cst.Arg(
            value=cst.Integer(value=str(function_metadata["iid"]))
        )
        val_arg = cst.Arg(
            value=updated_node.value, keyword=cst.Name(value="return_val")
        )
        function_name = cst.Arg(
            value=cst.SimpleString(
                value=self.__as_string(str(function_metadata["name"].value))
            )
        )
        arg_list = [ast_arg, iid_arg, function_iid_arg, function_name]
        if updated_node.value is not None:
            arg_list.append(val_arg)
        call = cst.Call(func=callee_name, args=arg_list)
        return updated_node.with_changes(
            value=call, whitespace_after_return=cst.SimpleWhitespace(" ")
        )

    def leave_Yield(self, original_node, updated_node):
        function_metadata = self.current_function[-1]
        if "yield" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_yield_")
        )
        self.to_import.add("_yield_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        function_metadata = self.current_function[-1]
        function_name = cst.Arg(
            value=cst.SimpleString(
                value=self.__as_string(str(function_metadata["name"].value))
            )
        )
        function_iid_arg = cst.Arg(
            value=cst.Integer(value=str(function_metadata["iid"]))
        )
        if m.matches(updated_node.value, m.From()):
            val_arg = cst.Arg(
                value=updated_node.value.item, keyword=cst.Name(value="return_val")
            )
        else:
            val_arg = cst.Arg(
                value=updated_node.value, keyword=cst.Name(value="return_val")
            )
        arg_list = [ast_arg, iid_arg, function_iid_arg, function_name]
        if updated_node.value is not None:
            arg_list.append(val_arg)
        call = cst.Call(func=callee_name, args=arg_list)
        if m.matches(updated_node.value, m.From()):
            return updated_node.with_changes(
                value=cst.From(item=call),
                whitespace_after_yield=cst.SimpleWhitespace(" "),
            )
        else:
            return updated_node.with_changes(
                value=call, whitespace_after_yield=cst.SimpleWhitespace(" ")
            )

    # def visit_Assert(self, node):
    #     return False

    def leave_Assert(self, original_node, updated_node):
        if "_assert" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_assert_")
        )
        self.to_import.add("_assert_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.test)
        arg_list = [ast_arg, iid_arg, val_arg]
        if updated_node.msg is not None:
            arg_list.append(cst.Arg(value=updated_node.msg))
        else:
            arg_list.append(cst.Arg(value=cst.Name("None")))
        call = cst.Call(func=callee_name, args=arg_list)
        return updated_node.with_changes(
            test=call, whitespace_after_assert=cst.SimpleWhitespace(" ")
        )

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call):
        if (
            ("pre_call" not in self.selected_hooks)
            and ("post_call" not in self.selected_hooks)
            or (
                m.matches(original_node.func, m.Name())
                and (
                    not (
                        self.__selected_by_decorators("pre_call", original_node.func)
                        or self.__selected_by_decorators(
                            "post_call", original_node.func
                        )
                    )
                )
            )
        ):
            return updated_node
        site_sensitive_functions = [
            "breakpoint",
            "dir",
            "eval",
            "exec",
            "globals",
            "help",
            "locals",
            "super",
            "vars",
        ]
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_call_")
        )
        self.to_import.add("_call_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        positional_args = cst.Arg(
            value=cst.List(
                elements=[
                    cst.Element(
                        value=cst.Tuple(
                            elements=[
                                cst.Element(
                                    value=cst.SimpleString(
                                        value=self.__as_string(a.star)
                                    )
                                ),
                                cst.Element(
                                    value=a.with_changes(
                                        comma=cst.MaybeSentinel.DEFAULT, star=""
                                    )
                                ),
                            ]
                        )
                    )
                    for a in updated_node.args
                    if a.keyword is None
                ]
            )
        )
        keyword_args = cst.Arg(
            value=cst.Dict(
                elements=[
                    cst.DictElement(
                        key=cst.SimpleString(value=self.__as_string(a.keyword.value)),
                        value=a.value,
                    )
                    for a in updated_node.args
                    if a.keyword is not None
                ]
            )
        )
        try:
            name_source = self.get_metadata(QualifiedNameProvider, original_node)
        except KeyError:
            name_source = []
        if (
            (len(list(name_source)) > 0)
            and (list(name_source)[0].source == QualifiedNameSource.BUILTIN)
            and (
                m.matches(original_node.func, m.Name())
                and original_node.func.value in site_sensitive_functions
            )
        ) or (
            any(a for a in updated_node.args if m.matches(a.value, m.GeneratorExp()))
        ):
            call_arg = cst.Arg(value=updated_node)
            only_post = cst.Arg(value=cst.Name("True"))
            call = cst.Call(
                func=callee_name,
                args=[
                    ast_arg,
                    iid_arg,
                    call_arg,
                    only_post,
                    cst.Arg(value=cst.Name("None")),
                    cst.Arg(value=cst.Name("None")),
                ],
                lpar=original_node.lpar,
                rpar=original_node.rpar,
            )
        else:
            call_arg = cst.Arg(value=updated_node.func)
            only_post = cst.Arg(value=cst.Name("False"))
            call = cst.Call(
                func=callee_name,
                args=[
                    ast_arg,
                    iid_arg,
                    call_arg,
                    only_post,
                    positional_args,
                    keyword_args,
                ],
                lpar=original_node.lpar,
                rpar=original_node.rpar,
            )
        return call

    # Exception
    def leave_Raise(self, original_node, updated_node):
        if "_raise" not in self.selected_hooks:
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_raise_")
        )
        self.to_import.add("_raise_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        arguments = [ast_arg, iid_arg]
        if updated_node.exc != None:
            exc_arg = cst.Arg(value=updated_node.exc, keyword=cst.Name(value="exc"))
            arguments.append(exc_arg)
        if updated_node.cause != None:
            cause_arg = cst.Arg(
                value=updated_node.cause.item, keyword=cst.Name(value="cause")
            )
            arguments.append(cause_arg)
        call = cst.Call(func=callee_name, args=arguments)
        return cst.Expr(value=call)

    def visit_Try(self, node):
        iid = self.__create_iid(node)
        self.current_try.append(iid)

    def leave_Try(self, original_node, updated_node):
        self.current_try.pop()
        if "try" not in self.selected_hooks:
            return updated_node
        enter_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_try_")
        )
        self.to_import.add("_try_")
        clean_exit = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_end_try_")
        )
        self.to_import.add("_end_try_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        enter_call = cst.Call(func=enter_name, args=[ast_arg, iid_arg])
        new_body = cst.IndentedBlock(
            body=[cst.SimpleStatementLine(body=[cst.Expr(value=enter_call)])]
            + list(updated_node.body.body)
        )
        end_call = cst.Call(func=clean_exit, args=[ast_arg, iid_arg])
        if updated_node.orelse != None:
            old_else = list(updated_node.orelse.body.body)
        else:
            old_else = []
        else_part = cst.Else(
            body=cst.IndentedBlock(
                body=old_else
                + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]
            )
        )

        if len(updated_node.handlers) == 0:
            new_handler = cst.ExceptHandler(
                body=cst.IndentedBlock(
                    body=[cst.SimpleStatementLine(body=[cst.Raise()])]
                )
            )
            return updated_node.with_changes(
                body=new_body, handlers=[new_handler], orelse=else_part
            )

        return updated_node.with_changes(body=new_body, orelse=else_part)

    def leave_ExceptHandler(self, original_node, updated_node):
        if "exception" not in self.selected_hooks:
            return updated_node
        exc_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_exc_")
        )
        self.to_import.add("_exc_")
        iid = self.current_try[-1]
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        exc_arg = cst.Arg(value=updated_node.type, keyword=cst.Name(value="exc"))
        arg_list = [ast_arg, iid_arg]
        if updated_node.type is not None:
            arg_list.append(exc_arg)
        if updated_node.name is not None:
            if m.matches(updated_node.name, m.AsName()):
                name_arg = cst.Arg(
                    value=updated_node.name.name, keyword=cst.Name(value="name")
                )
            else:
                name_arg = cst.Arg(
                    value=updated_node.name, keyword=cst.Name(value="name")
                )
            arg_list.append(name_arg)
        exc_call = cst.Call(func=exc_name, args=arg_list)
        new_body = cst.IndentedBlock(
            body=[cst.SimpleStatementLine(body=[cst.Expr(value=exc_call)])]
            + list(updated_node.body.body)
        )
        return updated_node.with_changes(body=new_body)

    # Control flow
    def leave_IndentedBlock(self, original_node, updated_node):
        if ("_break" not in self.selected_hooks) and (
            "_continue" not in self.selected_hooks
        ):
            return updated_node
        new_body = []
        for i in updated_node.body:
            if ("_break" in self.selected_hooks) and (
                m.matches(i, m.SimpleStatementLine(body=[m.Break()]))
            ):
                callee_name = cst.Attribute(
                    value=cst.Name(value="_rt"), attr=cst.Name(value="_break_")
                )
                self.to_import.add("_break_")
                iid = self.__create_iid(original_node)
                ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                call = cst.Call(func=callee_name, args=[ast_arg, iid_arg])
                condition = cst.If(
                    test=call,
                    body=cst.IndentedBlock(
                        body=[cst.SimpleStatementLine(body=[cst.Break()])]
                    ),
                )
                new_body.append(condition)
            elif ("_continue" in self.selected_hooks) and (
                m.matches(i, m.SimpleStatementLine(body=[m.Continue()]))
            ):
                callee_name = cst.Attribute(
                    value=cst.Name(value="_rt"), attr=cst.Name(value="_continue_")
                )
                self.to_import.add("_continue_")
                iid = self.__create_iid(original_node)
                ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                call = cst.Call(func=callee_name, args=[ast_arg, iid_arg])
                condition = cst.If(
                    test=call,
                    body=cst.IndentedBlock(
                        body=[cst.SimpleStatementLine(body=[cst.Continue()])]
                    ),
                )
                new_body.append(condition)
            else:
                new_body.append(i)

        return updated_node.with_changes(body=new_body)

    def leave_If(self, original_node, updated_node):
        if ("enter_if" not in self.selected_hooks) and (
            "exit_if" not in self.selected_hooks
        ):
            return updated_node
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if "enter_if" in self.selected_hooks:
            callee_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_enter_if_")
            )
            self.to_import.add("_enter_if_")
            val_arg = cst.Arg(value=updated_node.test)
            call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        else:
            call = updated_node.test
        if "exit_if" in self.selected_hooks:
            end_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_exit_if_")
            )
            self.to_import.add("_exit_if_")
            end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
            if m.matches(updated_node.body, m.SimpleStatementSuite()):
                new_body = cst.IndentedBlock(
                    body=[
                        cst.SimpleStatementLine(body=updated_node.body.body),
                        cst.SimpleStatementLine(body=[cst.Expr(value=end_call)]),
                    ]
                )
            else:
                new_body = cst.IndentedBlock(
                    body=list(updated_node.body.body)
                    + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]
                )

            if updated_node.orelse is None:
                new_orelse_body = [
                    cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])
                ]
            elif m.matches(updated_node.orelse.body, m.SimpleStatementSuite()):
                new_orelse_body = list(updated_node.orelse.body.body) + [
                    cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])
                ]
            else:
                new_orelse_body = list(updated_node.orelse.body.body) + [
                    cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])
                ]
            new_orelse = cst.Else(body=cst.IndentedBlock(body=new_orelse_body))
        else:
            new_body = updated_node.body
            new_orelse = updated_node.orelse
        return updated_node.with_changes(
            test=call,
            whitespace_before_test=cst.SimpleWhitespace(" "),
            body=new_body,
            orelse=new_orelse,
        )

    def leave_IfExp(self, original_node, updated_node):
        if (
            "enter_if" not in self.selected_hooks
            and "exit_if" not in self.selected_hooks
        ):
            return updated_node
        callee_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_if_expr_")
        )
        self.to_import.add("_if_expr_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        cond_arg = cst.Arg(value=updated_node.test)
        body_arg = cst.Arg(
            value=self.__wrap_in_lambda(original_node.body, updated_node.body)
        )
        orelse_arg = cst.Arg(
            value=self.__wrap_in_lambda(original_node.orelse, updated_node.orelse)
        )
        call = cst.Call(
            func=callee_name, args=[ast_arg, iid_arg, cond_arg, body_arg, orelse_arg]
        )
        return call

    def leave_While(self, original_node, updated_node):
        if ("enter_while" not in self.selected_hooks) and (
            "exit_while" not in self.selected_hooks
        ):
            return updated_node
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if "enter_while" in self.selected_hooks:
            enter_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_enter_while_")
            )
            self.to_import.add("_enter_while_")
            enter_arg = cst.Arg(value=updated_node.test)
            enter_call = cst.Call(func=enter_name, args=[ast_arg, iid_arg, enter_arg])
        else:
            enter_call = updated_node.test
        if "exit_while" in self.selected_hooks:
            end_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_exit_while_")
            )
            self.to_import.add("_exit_while_")
            end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
            if updated_node.orelse != None:
                old_else = updated_node.orelse.body.body
            else:
                old_else = []
            else_part = cst.Else(
                body=cst.IndentedBlock(
                    body=old_else
                    + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]
                )
            )
        else:
            else_part = updated_node.orelse
        return updated_node.with_changes(
            test=enter_call,
            whitespace_after_while=cst.SimpleWhitespace(" "),
            orelse=else_part,
        )

    def leave_For(self, original_node, updated_node):
        if ("enter_for" not in self.selected_hooks) and (
            "exit_for" not in self.selected_hooks
        ):
            return updated_node
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if "enter_for" in self.selected_hooks:
            generator_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_gen_")
            )
            self.to_import.add("_gen_")
            iter_arg = cst.Arg(value=updated_node.iter)
            generator_call = cst.Call(
                func=generator_name, args=[ast_arg, iid_arg, iter_arg]
            )
            else_part = updated_node.orelse
        elif "exit_for" in self.selected_hooks:
            end_name = cst.Attribute(
                value=cst.Name(value="_rt"), attr=cst.Name(value="_exit_for_")
            )
            self.to_import.add("_exit_for_")
            end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
            if updated_node.orelse != None:
                old_else = updated_node.orelse.body.body
            else:
                old_else = []
            else_part = cst.Else(
                body=cst.IndentedBlock(
                    body=list(old_else)
                    + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]
                )
            )
            generator_call = updated_node.iter
        return updated_node.with_changes(
            iter=generator_call, orelse=else_part, target=original_node.target
        )

    def leave_CompFor(self, original_node, updated_node):
        if (
            "enter_for" not in self.selected_hooks
            and "exit_for" not in self.selected_hooks
        ):
            return updated_node
        generator_name = cst.Attribute(
            value=cst.Name(value="_rt"), attr=cst.Name(value="_gen_")
        )
        self.to_import.add("_gen_")
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name("_dynapyt_ast_"))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        iter_arg = cst.Arg(value=updated_node.iter)
        generator_call = cst.Call(
            func=generator_name, args=[ast_arg, iid_arg, iter_arg]
        )
        return updated_node.with_changes(
            iter=generator_call, target=original_node.target
        )
