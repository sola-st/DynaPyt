from operator import mod
from string import whitespace
import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider, QualifiedNameProvider
import libcst.matchers as m
from libcst.matchers import call_if_not_inside, call_if_inside
import libcst.helpers as helpers
from libcst.metadata.expression_context_provider import ExpressionContext
from libcst.metadata.scope_provider import QualifiedNameSource, ClassScope
from numpy import isin


class CodeInstrumenter(m.MatcherDecoratableTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider, QualifiedNameProvider,)

    # Internal
    def __init__(self, src, file_path, iids, selected_hooks):
        super().__init__()
        self.source = src
        self.file_path = file_path
        self.iids = iids
        self.name_stack = []
        self.current_try = []
        self.current_class = []
        self.selected_hooks = selected_hooks
        self.to_import = set()

    def __create_iid(self, node):
        location = self.get_metadata(PositionProvider, node)
        start_line = location.start.line
        start_column = location.start.column
        end_line = location.end.line
        end_column = location.end.column
        iid = self.iids.new(self.file_path, start_line, start_column, end_line, end_column)
        return iid

    def __create_import(self, names):
        module_name = cst.Attribute(value= cst.Name(value='dynapyt'), attr=cst.Name(value="runtime"))
        imp_aliases = [cst.ImportAlias(name=cst.Name(value=name)) for name in names]
        imp = cst.ImportFrom(module=module_name, names=imp_aliases)
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt
    
    def __wrap_in_lambda(self, original_node, updated_node):
        if m.matches(updated_node, m.Call(func=m.Name('super'), args=[])):
            class_arg = cst.Arg(value=cst.Name(value=self.current_class[-1]))
            new_node = updated_node.with_changes(args=[class_arg, cst.Arg(value=cst.Name('self'))])
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
                if (n.value not in unique_names) and (my_scope == n_scope) and (len(list(name_source)) > 0) and (list(name_source)[0].source == QualifiedNameSource.LOCAL):
                    parameters.append(cst.Param(name=cst.Name(value=n.value), default=cst.Name(value=n.value)))
                    unique_names.add(n.value)
        lambda_expr = cst.Lambda(params=cst.Parameters(params=parameters), body=updated_node)
        return lambda_expr
    
    def __as_string(self, s):
        if hasattr(self, 'quote') and self.quote == '"':
            return "'" + s + "'"
        else:
            return '"' + s + '"'
    
    def visit_Annotation(self, node):
        return False
    
    def visit_Decorator(self, node):
        return False
    
    def leave_Tuple(self, original_node, updated_node):
        if len(updated_node.lpar) == 0:
            return updated_node.with_changes(lpar=[cst.LeftParen()], rpar=[cst.RightParen()])
        return updated_node

    # Top level

    def leave_Module(self, original_node, updated_node):
        imports_index = -1
        # '\"\"\"' + self.source.replace('\"', '\\"') + '\"\"\"'
        # source_code = cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(cst.Name('_dynapyt_source_code_'))], value=cst.SimpleString(value=repr(self.source)))])
        # parse_to_ast = cst.Call(func=cst.Name('_dynapyt_parse_to_ast_'), args=[cst.Arg(cst.Name('_dynapyt_source_code_'))])
        parse_to_ast = cst.BinaryOperation(left=cst.Name(value='__file__'), operator=cst.Add(), right=cst.SimpleString('".orig"'))
        get_ast = cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(cst.Name('_dynapyt_ast_'))], value=parse_to_ast)])
        dynapyt_imports = [cst.Newline(value='\n')]
        # dynapyt_imports.append(self.__create_import(["_dynapyt_parse_to_ast_"]))
        dynapyt_imports.append(self.__create_import(["_catch_"]))
        import_names = list(self.to_import)
        for i in range(len(updated_node.body)):
            if m.matches(updated_node.body[i], m.SimpleStatementLine()) and m.matches(updated_node.body[i].body[0], m.ImportFrom(module=m.Name(value='__future__'))):
                imports_index = i
        # if 'assignment' in self.selected_hooks:
        #     import_names.append("_assign_")
        # if 'expression' in self.selected_hooks:
        #     import_names.append("_expr_")
        # if 'binary_operation' in self.selected_hooks:
        #     import_names.append("_binary_op_")
        # if 'unary_operation' in self.selected_hooks:
        #     import_names.append("_unary_op_")
        # if 'comparison' in self.selected_hooks:
        #     import_names.append("_comp_op_")
        # if 'call' in self.selected_hooks:
        #     import_names.append("_call_")
        # if 'literal' in self.selected_hooks:
        #     import_names.append("_literal_")
        # if 'exception' in self.selected_hooks:
        #     import_names.append("_raise_")
        # if 'read' in self.selected_hooks:
        #     import_names.append("_read_var_")
        # if 'control_flow' in self.selected_hooks:
        #     import_names.append("_condition_")
        #     import_names.append("_enter_ctrl_flow_")
        #     import_names.append("_exit_ctrl_flow_")
        #     import_names.append("_jump_")
        #     import_names.append("_gen_")
        # if 'function' in self.selected_hooks:
        #     import_names.append("_func_entry_")
        #     import_names.append("_func_exit_")
        if len(import_names) > 0:
            dynapyt_imports.append(self.__create_import(import_names))
            dynapyt_imports.append(cst.Newline(value='\n'))
        code_body = list(updated_node.body[imports_index+1:])
        handler_call = cst.Call(func=cst.Name(value='_catch_'), args=[cst.Arg(cst.Name('_dynapyt_exception_'))])
        handler_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=handler_call)])])
        try_body = cst.Try(body=cst.IndentedBlock(body=code_body), handlers=[cst.ExceptHandler(body=handler_body, type=cst.Name(value='Exception'), name=cst.AsName(cst.Name(value='_dynapyt_exception_')))])
        # new_body = list(updated_node.body[:imports_index+1]) + dynapyt_imports + [source_code, get_ast] + [try_body]
        new_body = list(updated_node.body[:imports_index+1]) + dynapyt_imports + [get_ast] + [try_body]
        return updated_node.with_changes(body=new_body)
    
    def visit_ClassDef(self, node):
        self.current_class.append(node.name.value)
    
    def leave_ClassDef(self, original_node, updated_node):
        self.current_class.pop()
        return updated_node

    def leave_Expr(self, original_node, updated_node):
        if 'expression' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_expr_')
        self.to_import.add('_expr_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(self.__wrap_in_lambda(original_node, updated_node))
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return updated_node.with_changes(value=call)

    # Lowest level
    @call_if_not_inside(m.AssignTarget() | m.Import() | m.ImportFrom() | m.AnnAssign())
    def leave_Name(self, original_node, updated_node):
        if ('boolean' in self.selected_hooks) and (updated_node.value in ['True', 'False']):
            callee_name = cst.Name(value='_bool_')
            self.to_import.add('_bool_')
            iid = self.__create_iid(original_node)
            ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            val_arg = cst.Arg(value=updated_node)
            call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
            return call

        if 'read' not in self.selected_hooks:
            return updated_node
        try:
            context = self.get_metadata(ExpressionContextProvider, original_node)
            name_source = self.get_metadata(QualifiedNameProvider, original_node)
        except KeyError:
            context = -1
            name_source = []
        if len(list(name_source)) == 0:
            return updated_node
        if (context == ExpressionContext.LOAD) and (list(name_source)[0].source == QualifiedNameSource.LOCAL):
            callee_name = cst.Name(value='_read_')
            self.to_import.add('_read_')
            iid = self.__create_iid(original_node)
            ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            var_arg = cst.Arg(value=self.__wrap_in_lambda(original_node, updated_node))
            call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, var_arg])
            return call
        else:
            return updated_node
    
    def leave_Integer(self, original_node, updated_node):
        if 'integer' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_int_')
        self.to_import.add('_int_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return call
    
    def leave_Float(self, original_node, updated_node):
        if 'float' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_float_')
        self.to_import.add('_float_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return call
    
    def leave_Imaginary(self, original_node, updated_node):
        if 'imaginary' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_img_')
        self.to_import.add('_img_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return call

    def visit_ConcatenatedString(self, node):
        return False

    def leave_ConcatenatedString(self, original_node, updated_node):
        if ('string' not in self.selected_hooks) and ('literal' not in self.selected_hooks):
            return updated_node

        callee_name = cst.Name(value='_str_')
        self.to_import.add('_str_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])

        return call

    @call_if_not_inside(m.FormattedStringExpression() | m.ConcatenatedString())
    def visit_FormattedString(self, node):
        self.quote = node.end
        return True

    @call_if_not_inside(m.FormattedStringExpression() | m.ConcatenatedString())
    def leave_FormattedString(self, original_node, updated_node):
        self.quote = ''
        if 'string' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_str_')
        self.to_import.add('_str_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return call
    
    @call_if_not_inside(m.ConcatenatedString())
    @call_if_inside(m.Assign() | m.AugAssign() | m.Arg() | m.BinaryOperation())
    def leave_SimpleString(self, original_node, updated_node):
        if 'string' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_str_')
        self.to_import.add('_str_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return call

    # Memory access
    def leave_Del(self, original_node, updated_node):
        if 'delete' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_delete_')
        self.to_import.add('_delete_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        target_arg = cst.Arg(value=self.__wrap_in_lambda(original_node.target, updated_node.target))
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, target_arg])
        return cst.Expr(value=call)
    
    @call_if_not_inside(m.AssignTarget() | m.AnnAssign())
    def leave_Subscript(self, original_node, updated_node):
        if 'subscript' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_sub_')
        self.to_import.add('_sub_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        name_arg = cst.Arg(updated_node.value)
        slices = []
        for i in updated_node.slice:
            if m.matches(i.slice, m.Slice()):
                slices.append(cst.Element(cst.Call(func=cst.Name('slice'), args=[
                    cst.Arg(i.slice.lower if i.slice.lower != None else cst.Name('None')),
                    cst.Arg(i.slice.upper if i.slice.upper != None else cst.Name('None')),
                    cst.Arg(i.slice.step if i.slice.step != None else cst.Name('None'))])))
            else:
                slices.append(cst.Element(i.slice.value))
        slice_arg = cst.Arg(cst.List(elements=slices))
        return cst.Call(func=callee_name, args=[ast_arg, iid_arg, name_arg, slice_arg])
    
    @call_if_not_inside(m.AssignTarget() | m.Import() | m.ImportFrom() | m.AnnAssign())
    def leave_Attribute(self, original_node, updated_node):
        if 'attribute' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_attr_')
        self.to_import.add('_attr_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        base_arg = cst.Arg(updated_node.value)
        attr_arg = cst.Arg(cst.SimpleString(value=self.__as_string(str(updated_node.attr.value))))
        return cst.Call(func=callee_name, args=[ast_arg, iid_arg, base_arg, attr_arg])

    # Operations
    def leave_BinaryOperation(self, original_node, updated_node):
        if ('binary_operation' not in self.selected_hooks) and (type(original_node.operator).__name__ not in self.selected_hooks):
            return updated_node
        bin_op = {'Add': 0, 'BitAnd': 1, 'BitOr': 2, 'BitXor': 3, 'Divide': 4,
            'FloorDivide': 5, 'LeftShift': 6, 'MatrixMultiply': 7, 'Modulo': 8,
            'Multiply': 9, 'Power': 10, 'RightShift': 11, 'Subtract': 12}
        callee_name = cst.Name(value="_binary_op_")
        self.to_import.add('_binary_op_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(self.__wrap_in_lambda(original_node.left, updated_node.left))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bin_op[operator_name])))
        right_arg = cst.Arg(self.__wrap_in_lambda(original_node.right, updated_node.right))
        call = cst.Call(func=callee_name, args=[
                        ast_arg, iid_arg, left_arg, operator_arg, right_arg])
        return call

    def leave_BooleanOperation(self, original_node, updated_node):
        if ('boolean_operation' not in self.selected_hooks) and (type(original_node.operator).__name__ not in self.selected_hooks):
            return updated_node
        bool_op = {'And': 13, 'Or': 14}
        callee_name = cst.Name(value='_binary_op_')
        self.to_import.add('_binary_op_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(self.__wrap_in_lambda(original_node.left, updated_node.left))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bool_op[operator_name])))
        right_arg = cst.Arg(self.__wrap_in_lambda(original_node.right, updated_node.right))
        call = cst.Call(func=callee_name, args=[
                        ast_arg, iid_arg, left_arg, operator_arg, right_arg])
        return call
    
    def leave_UnaryOperation(self, original_node, updated_node):
        if ('unary_operation' not in self.selected_hooks) and (type(original_node.operator).__name__ not in self.selected_hooks):
            return updated_node
        un_op = {'BitInvert': 0, 'Minus': 1, 'Not': 2, 'Plus': 3}
        callee_name = cst.Name(value='_unary_op_')
        self.to_import.add('_unary_op_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(un_op[operator_name])))
        right_arg = cst.Arg(updated_node.expression)
        call = cst.Call(func=callee_name, args=[
                        ast_arg, iid_arg, operator_arg, right_arg])
        return call
    
    def leave_Comparison(self, original_node, updated_node):
        if ('comparison' not in self.selected_hooks) and (not any(type(i.operator).__name__ in self.selected_hooks for i in updated_node.comparisons)):
            return updated_node
        comp_op = {'Equal': 0, 'GreaterThan': 1, 'GreaterThanEqual': 2, 'In': 3,
            'Is': 4, 'LessThan': 5, 'LessThanEqual': 6, 'NotEqual': 7,
            'IsNot': 8, 'NotIn': 9}
        callee_name = cst.Name(value='_comp_op_')
        self.to_import.add('_comp_op_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        comparisons = []
        for i in updated_node.comparisons:
            operator_name = type(i.operator).__name__
            comparisons.append(cst.Element(value=cst.Tuple(elements=[cst.Element(cst.Integer(str(comp_op[operator_name]))), cst.Element(i.comparator)])))
        call = cst.Call(func=callee_name, args=[
                        ast_arg, iid_arg, left_arg, cst.Arg(cst.List(elements=comparisons))])
        return call
    
    def leave_Assign(self, original_node, updated_node):
        if 'assignment' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_assign_')
        self.to_import.add('_assign_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(value=cst.List(elements=[cst.Element(self.__wrap_in_lambda(tu.target, tu.target)) for to, tu in zip(original_node.targets, updated_node.targets)]))
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg, left_arg])
        # new_targets = [t for t in original_node.targets if m.matches(t, m.AssignTarget(target=m.Name()))]
        # old_targets = []
        # for i in range(len(original_node.targets)):
        #     if not m.matches(original_node.targets[i], m.AssignTarget(target=m.Name())):
        #         old_targets.append(updated_node.targets[i])
        return updated_node.with_changes(value=call)
    
    def leave_AugAssign(self, original_node, updated_node):
        if ('assignment' not in self.selected_hooks) and (type(original_node.operator).__name__ not in self.selected_hooks):
            return updated_node
        aug_op = {'AddAssign': 0, 'BitAndAssign': 1, 'BitOrAssign': 2, 'BitXorAssign': 3, 'DivideAssign': 4,
            'FloorDivideAssign': 5, 'LeftShiftAssign': 6, 'MatrixMultiplyAssign': 7, 'ModuloAssign': 8,
            'MultiplyAssign': 9, 'PowerAssign': 10, 'RightShiftAssign': 11, 'SubtractAssign': 12}
        callee_name = cst.Name(value='_aug_assign_')
        self.to_import.add('_aug_assign_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        opr_arg = cst.Arg(value=cst.Integer(value=str(aug_op[operator_name])))
        val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(value=self.__wrap_in_lambda(original_node.target, updated_node.target))
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, left_arg, opr_arg, val_arg])
        return updated_node.with_changes(value=call, target=original_node.target)
    
    # Function
    def leave_FunctionDef(self, original_node, updated_node):
        if 'function' not in self.selected_hooks:
            return updated_node
        enter_name = cst.Name(value='_func_entry_')
        self.to_import.add('_func_entry_')
        exit_name = cst.Name(value='_func_exit_')
        self.to_import.add('_func_exit_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        args_arg = cst.Arg(value=cst.List(elements=[cst.Element(value=self.__wrap_in_lambda(po.name, pu.name)) for po, pu in zip(original_node.params.params, updated_node.params.params)]))
        entry_stmt = cst.Expr(cst.Call(func=enter_name, args=[ast_arg, iid_arg, args_arg]))
        exit_stmt = cst.Expr(cst.Call(func=exit_name, args=[ast_arg, iid_arg]))
        if m.matches(updated_node.body.body[0], m.SimpleStatementLine(body=[m.Expr(value=m.SimpleString())])):
            new_body = updated_node.body.with_changes(body=[updated_node.body.body[0], cst.SimpleStatementLine([entry_stmt])]+list(updated_node.body.body[1:])+[cst.SimpleStatementLine([exit_stmt])])
        else:
            new_body = updated_node.body.with_changes(body=[cst.SimpleStatementLine([entry_stmt])]+list(updated_node.body.body)+[cst.SimpleStatementLine([exit_stmt])])
        new_node = updated_node
        return new_node.with_changes(body=new_body)
    
    def leave_Lambda(self, original_node, updated_node):
        if 'lambda' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_lambda_')
        self.to_import.add('_lambda_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        args_arg = cst.Arg(value=cst.List(elements=[cst.Element(value=self.__wrap_in_lambda(po.name, pu.name)) for po, pu in zip(original_node.params.params, updated_node.params.params)]))
        body_arg = cst.Arg(value=self.__wrap_in_lambda(original_node.body, updated_node.body))
        new_stmt = cst.Call(func=callee_name, args=[ast_arg, iid_arg, args_arg, body_arg])
        return updated_node.with_changes(body=new_stmt)
    
    def leave_Return(self, original_node, updated_node):
        if 'return' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_return_')
        self.to_import.add('_return_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.value, keyword=cst.Name(value='return_val'))
        arg_list = [ast_arg, iid_arg]
        if updated_node.value is not None:
            arg_list.append(val_arg)
        call = cst.Call(func=callee_name, args=arg_list)
        return updated_node.with_changes(value=call, whitespace_after_return=cst.SimpleWhitespace(' '))
    
    def leave_Yield(self, original_node, updated_node):
        if 'yield' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_yield_')
        self.to_import.add('_yield_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        if m.matches(updated_node.value, m.From()):
            val_arg = cst.Arg(value=updated_node.value.item, keyword=cst.Name(value='return_val'))
        else:
            val_arg = cst.Arg(value=updated_node.value, keyword=cst.Name(value='return_val'))
        arg_list = [ast_arg, iid_arg]
        if updated_node.value is not None:
            arg_list.append(val_arg)
        call = cst.Call(func=callee_name, args=arg_list)
        if m.matches(updated_node.value, m.From()):
            return updated_node.with_changes(value=cst.From(item=call), whitespace_after_yield=cst.SimpleWhitespace(' '))
        else:
            return updated_node.with_changes(value=call, whitespace_after_yield=cst.SimpleWhitespace(' '))
    
    def leave_Call(self, original_node, updated_node):
        if 'call' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_call_')
        self.to_import.add('_call_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        call_arg = cst.Arg(value=self.__wrap_in_lambda(original_node, updated_node))
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, call_arg])
        return call
    
    # Exception
    def leave_Raise(self, original_node, updated_node):
        if 'exception' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_raise_')
        self.to_import.add('_raise_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        arguments = [ast_arg, iid_arg]
        if updated_node.exc != None:
            exc_arg = cst.Arg(value=updated_node.exc, keyword=cst.Name(value='exc'))
            arguments.append(exc_arg)
        if updated_node.cause != None:
            cause_arg = cst.Arg(value=updated_node.cause.item, keyword=cst.Name(value='cause'))
            arguments.append(cause_arg)
        call = cst.Call(func=callee_name, args=arguments)
        return cst.Expr(value=call)
    
    def visit_Try(self, node):
        iid = self.__create_iid(node)
        self.current_try.append(iid)

    def leave_Try(self, original_node, updated_node):
        self.current_try.pop()
        if 'exception' not in self.selected_hooks:
            return updated_node
        enter_name = cst.Name(value='_try_')
        self.to_import.add('_try_')
        clean_exit = cst.Name(value='_end_try_')
        self.to_import.add('_end_try_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        enter_call = cst.Call(func=enter_name, args=[ast_arg, iid_arg])
        new_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=enter_call)])] + list(updated_node.body.body))
        end_call = cst.Call(func=clean_exit, args=[ast_arg, iid_arg])
        if updated_node.orelse != None:
            old_else = list(updated_node.orelse.body.body)
        else:
            old_else = []
        else_part = cst.Else(body=cst.IndentedBlock(body=old_else + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))

        if len(updated_node.handlers) == 0:
            new_handler = cst.ExceptHandler(body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Raise()])]))
            return updated_node.with_changes(body=new_body, handlers=[new_handler], orelse=else_part)    
        
        return updated_node.with_changes(body=new_body, orelse=else_part)
    
    def leave_ExceptHandler(self, original_node, updated_node):
        if 'exception' not in self.selected_hooks:
            return updated_node
        exc_name = cst.Name(value='_exc_')
        self.to_import.add('_exc_')
        iid = self.current_try[-1]
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        exc_arg = cst.Arg(value=updated_node.type, keyword=cst.Name(value='exc'))
        arg_list = [ast_arg, iid_arg]
        if updated_node.type is not None:
            arg_list.append(exc_arg)
        if updated_node.name is not None:
            if m.matches(updated_node.name, m.AsName()):
                name_arg = cst.Arg(value=updated_node.name.name, keyword=cst.Name(value='name'))
            else:
                name_arg = cst.Arg(value=updated_node.name, keyword=cst.Name(value='name'))
            arg_list.append(name_arg)
        exc_call = cst.Call(func=exc_name, args=arg_list)
        new_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=exc_call)])] + list(updated_node.body.body))
        return updated_node.with_changes(body=new_body)
    
    # Control flow
    def leave_IndentedBlock(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        new_body = []
        for i in updated_node.body:
            if m.matches(i, m.SimpleStatementLine(body=[m.Break()])):
                callee_name = cst.Name(value='_break_')
                self.to_import.add('_break_')
                iid = self.__create_iid(original_node)
                ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                call = cst.Call(func=callee_name, args=[ast_arg, iid_arg])
                condition = cst.If(test=call, body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Break()])]))
                new_body.append(condition)
            elif m.matches(i, m.SimpleStatementLine(body=[m.Continue()])):
                callee_name = cst.Name(value='_continue_')
                self.to_import.add('_continue_')
                iid = self.__create_iid(original_node)
                ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                call = cst.Call(func=callee_name, args=[ast_arg, iid_arg])
                condition = cst.If(test=call, body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Continue()])]))
                new_body.append(condition)
            else:
                new_body.append(i)

        return updated_node.with_changes(body=new_body)
    
    def leave_If(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_enter_ctrl_flow_')
        self.to_import.add('_enter_ctrl_flow_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.test)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        end_name = cst.Name(value='_exit_ctrl_flow_')
        self.to_import.add('_exit_ctrl_flow_')
        end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
        return updated_node.with_changes(test=call, body=cst.IndentedBlock(body=updated_node.body.body + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))

    def leave_IfExp(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value='_condition_')
        self.to_import.add('_condition_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.test)
        call = cst.Call(func=callee_name, args=[ast_arg, iid_arg, val_arg])
        return updated_node.with_changes(test=call)

    def leave_While(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        enter_name = cst.Name(value='_enter_ctrl_flow_')
        self.to_import.add('_enter_ctrl_flow_')
        enter_arg = cst.Arg(value=updated_node.test)
        enter_call = cst.Call(func=enter_name, args=[ast_arg, iid_arg, enter_arg])
        end_name = cst.Name(value='_exit_ctrl_flow_')
        self.to_import.add('_exit_ctrl_flow_')
        end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
        if updated_node.orelse != None:
            old_else = updated_node.orelse.body.body
        else:
            old_else = []
        else_part = cst.Else(body=cst.IndentedBlock(body=old_else + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))
        return updated_node.with_changes(test=enter_call, orelse=else_part)
    
    def leave_For(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        generator_name = cst.Name(value='_gen_')
        self.to_import.add('_gen_')
        end_name = cst.Name(value='_exit_ctrl_flow_')
        self.to_import.add('_exit_ctrl_flow_')
        iid = self.__create_iid(original_node)
        ast_arg = cst.Arg(value=cst.Name('_dynapyt_ast_'))
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        iter_arg = cst.Arg(value=updated_node.iter)
        generator_call = cst.Call(func=generator_name, args=[ast_arg, iid_arg, iter_arg])
        end_call = cst.Call(func=end_name, args=[ast_arg, iid_arg])
        if updated_node.orelse != None:
            old_else = updated_node.orelse.body.body
        else:
            old_else = []
        else_part = cst.Else(body=cst.IndentedBlock(body=old_else + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))
        return updated_node.with_changes(iter=generator_call, orelse=else_part)