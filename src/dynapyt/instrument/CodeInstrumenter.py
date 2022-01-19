import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider, QualifiedNameProvider
import libcst.matchers as matchers
import libcst.helpers as helpers
from libcst.metadata.expression_context_provider import ExpressionContext
from libcst.metadata.scope_provider import QualifiedNameSource


class CodeInstrumenter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider, QualifiedNameProvider,)

    def __init__(self, src, file_path, iids, selected_hooks):
        self.source = src
        self.file_path = file_path
        self.iids = iids
        self.name_stack = []
        self.selected_hooks = selected_hooks

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
    
    def __wrap_in_lambda(self, node):
        # used_names = set(map(lambda x: x.value, matchers.findall(node, matchers.Name())))
        parameters = []
        # for n in used_names:
        #     parameters.append(cst.Param(name=cst.Name(value=n), default=cst.Name(value=n)))
        lambda_expr = cst.Lambda(params=cst.Parameters(params=parameters), body=node)
        return lambda_expr

    def leave_Module(self, original_node, updated_node):
        source_code = cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(cst.Name('_dynapyt_source_code_'))], value=cst.SimpleString(value='\"\"\"\n' + self.source + '\n\"\"\"'))])
        parse_to_ast = cst.Call(func=cst.Name('_dynapyt_parse_to_ast_'), args=[cst.Arg(cst.Name('_dynapyt_source_code_'))])
        get_ast = cst.SimpleStatementLine(body=[cst.Assign(targets=[cst.AssignTarget(cst.Name('_dynapyt_ast_'))], value=parse_to_ast)])
        imports_index = -1
        for i in range(len(updated_node.body)):
            if isinstance(updated_node.body[i].body, (tuple, list)):
                if isinstance(updated_node.body[i].body[0], (cst.Import, cst.ImportFrom)):
                    imports_index = i
                elif i == 0:
                    continue
                else:
                    break
            else:
                break
        dynapyt_imports = [cst.Newline(value='\n')]
        dynapyt_imports.append(self.__create_import(["_dynapyt_parse_to_ast_"]))
        dynapyt_imports.append(self.__create_import(["_catch_"]))
        import_names = []
        if 'assignment' in self.selected_hooks:
            import_names.append("_assign_")
        if 'expression' in self.selected_hooks:
            import_names.append("_expr_")
        if 'binary_operation' in self.selected_hooks:
            import_names.append("_binary_op_")
        if 'unary_operation' in self.selected_hooks:
            import_names.append("_unary_op_")
        if 'comparison' in self.selected_hooks:
            import_names.append("_comp_op_")
        if 'call' in self.selected_hooks:
            import_names.append("_call_")
        if 'literal' in self.selected_hooks:
            import_names.append("_literal_")
        if 'exception' in self.selected_hooks:
            import_names.append("_raise_")
        if 'read' in self.selected_hooks:
            import_names.append("_read_var_")
        if 'control_flow' in self.selected_hooks:
            import_names.append("_condition_")
            import_names.append("_enter_ctrl_flow_")
            import_names.append("_exit_ctrl_flow_")
            import_names.append("_jump_")
        if 'function' in self.selected_hooks:
            import_names.append("_func_entry_")
            import_names.append("_func_exit_")
        dynapyt_imports.append(self.__create_import(import_names))
        dynapyt_imports.append(cst.Newline(value='\n'))
        code_body = list(updated_node.body[imports_index+1:])
        handler_call = cst.Call(func=cst.Name(value='_catch_'), args=[cst.Arg(cst.Name('_dynapyt_exception_'))])
        handler_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=handler_call)])])
        try_body = cst.Try(body=cst.IndentedBlock(body=code_body), handlers=[cst.ExceptHandler(body=handler_body, type=cst.Name(value='Exception'), name=cst.AsName(cst.Name(value='_dynapyt_exception_')))])
        new_body = list(updated_node.body[:imports_index+1]) + dynapyt_imports + [source_code, get_ast] + [try_body]
        return updated_node.with_changes(body=new_body)

    def leave_Name(self, original_node, updated_node):
        if ('literal' in self.selected_hooks) and (updated_node.value in ['True', 'False']):
            callee_name = cst.Name(value="_literal_")
            iid = self.__create_iid(original_node)
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            val_arg = cst.Arg(value=updated_node)
            call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
            return call

        if 'read' not in self.selected_hooks:
            return updated_node
        context = self.get_metadata(ExpressionContextProvider, original_node)
        # print(original_node, context, context == ExpressionContext.LOAD)
        name_source = self.get_metadata(QualifiedNameProvider, original_node)
        if len(list(name_source)) == 0:
            return updated_node
        if (context == ExpressionContext.LOAD) and (list(name_source)[0].source == QualifiedNameSource.LOCAL):
            callee_name = cst.Name(value="_read_var_")
            iid = self.__create_iid(original_node)
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            name_arg = cst.Arg(value=cst.SimpleString(value='"'+original_node.value+'"'))
            var_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
            call = cst.Call(func=callee_name, args=[iid_arg, name_arg, var_arg])
            return call
        else:
            return updated_node
    
    def leave_Integer(self, original_node, updated_node):
        if 'literal' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_literal_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=cst.Integer(value=original_node.value))
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return call
    
    def leave_Float(self, original_node, updated_node):
        if 'literal' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_literal_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=cst.Float(value=original_node.value))
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return call
    
    def leave_SimpleString(self, original_node, updated_node):
        if 'literal' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_literal_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=cst.SimpleString(value=original_node.value))
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return call

    def leave_BinaryOperation(self, original_node, updated_node):
        if 'binary_operation' not in self.selected_hooks:
            return updated_node
        bin_op = {'Add': 0, 'BitAnd': 1, 'BitOr': 2, 'BitXor': 3, 'Divide': 4,
            'FloorDivide': 5, 'LeftShift': 6, 'MatrixMultiply': 7, 'Modulo': 8,
            'Multiply': 9, 'Power': 10, 'RightShift': 11, 'Subtract': 12}
        callee_name = cst.Name(value="_binary_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bin_op[operator_name])))
        right_arg = cst.Arg(updated_node.right)
        call = cst.Call(func=callee_name, args=[
                        iid_arg, left_arg, operator_arg, right_arg])
        return call

    def leave_BooleanOperation(self, original_node, updated_node):
        if 'boolean_operation' not in self.selected_hooks:
            return updated_node
        bool_op = {'And': 0, 'Or': 1}
        callee_name = cst.Name(value="_binary_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(bool_op[operator_name])))
        right_arg = cst.Arg(updated_node.right)
        call = cst.Call(func=callee_name, args=[
                        iid_arg, left_arg, operator_arg, right_arg])
        return call
    
    def leave_UnaryOperation(self, original_node, updated_node):
        if 'unary_operation' not in self.selected_hooks:
            return updated_node
        un_op = {'BitInvert': 0, 'Minus': 1, 'Not': 2, 'Plus': 3}
        callee_name = cst.Name(value="_unary_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.Integer(str(un_op[operator_name])))
        right_arg = cst.Arg(updated_node.expression)
        call = cst.Call(func=callee_name, args=[
                        iid_arg, operator_arg, right_arg])
        return call
    
    def leave_Comparison(self, original_node, updated_node):
        if 'comparison' not in self.selected_hooks:
            return updated_node
        comp_op = {'Equal': 0, 'GreaterThan': 1, 'GreaterThanEqual': 2, 'In': 3,
            'Is': 4, 'LessThan': 5, 'LessThanEqual': 6, 'NotEqual': 7,
            'IsNot': 8, 'NotIn': 9}
        callee_name = cst.Name(value="_comp_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        comparisons = []
        for i in updated_node.comparisons:
            operator_name = type(i.operator).__name__
            comparisons.append(cst.Element(value=cst.Tuple(elements=[cst.Element(cst.Integer(str(comp_op[operator_name]))), cst.Element(i.comparator)])))
        call = cst.Call(func=callee_name, args=[
                        iid_arg, left_arg, cst.Arg(cst.List(elements=comparisons))])
        return call
    
    def leave_Assign(self, original_node, updated_node):
        if 'assignment' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_assign_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(value=cst.List(elements=[cst.Element(t.target) for t in updated_node.targets]))
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return updated_node.with_changes(value=call)
    
    def leave_AugAssign(self, original_node, updated_node):
        if 'assignment' not in self.selected_hooks:
            return updated_node
        aug_op = {'AddAssign': 0, 'BitAndAssign': 1, 'BitOrAssign': 2, 'BitXorAssign': 3, 'DivideAssign': 4,
            'FloorDivideAssign': 5, 'LeftShiftAssign': 6, 'MatrixMultiplyAssign': 7, 'ModuloAssign': 8,
            'MultiplyAssign': 9, 'PowerAssign': 10, 'RightShiftAssign': 11, 'SubtractAssign': 12}
        callee_name = cst.Name(value="_assign_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        opr_arg = cst.Arg(value=cst.Integer(value=str(aug_op[operator_name])))
        val_arg = cst.Arg(value=updated_node.value)
        left_arg = cst.Arg(value=cst.List(elements=[cst.Element(updated_node.target)]))
        call = cst.Call(func=callee_name, args=[iid_arg, left_arg, val_arg, opr_arg])
        return updated_node.with_changes(value=call)
    
    def leave_Expr(self, original_node, updated_node):
        if 'expression' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_expr_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(original_node)
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return updated_node.with_changes(value=call)
    
    def leave_FunctionDef(self, original_node, updated_node):
        if 'function' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_func_entry_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        entry_stmt = cst.Expr(cst.Call(func=callee_name, args=[iid_arg]))
        new_body = updated_node.body.with_changes(body=[cst.SimpleStatementLine([entry_stmt])]+list(updated_node.body.body))
        new_node = updated_node
        return new_node.with_changes(body=new_body)
    
    def leave_Return(self, original_node, updated_node):
        if 'function' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_func_exit_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.value)
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return updated_node.with_changes(value=call)
    
    def leave_Del(self, original_node, updated_node):
        if 'delete' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_delete_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        del_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[iid_arg, del_arg])
        return call
    
    def leave_Call(self, original_node, updated_node):
        if 'call' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_call_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        call_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[iid_arg, call_arg])
        return call
    
    def leave_Raise(self, original_node, updated_node):
        if 'exception' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_raise_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        raise_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[iid_arg, raise_arg])
        return call
    
    def leave_If(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_enter_ctrl_flow_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.test)
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        end_name = cst.Name(value="_exit_ctrl_flow_")
        end_call = cst.Call(func=end_name, args=[iid_arg])
        return updated_node.with_changes(test=call, body= cst.IndentedBlock(body=updated_node.body.body + [cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))

    def leave_IfExp(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_condition_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        val_arg = cst.Arg(value=updated_node.test)
        call = cst.Call(func=callee_name, args=[iid_arg, val_arg])
        return updated_node.with_changes(test=call)

    def leave_While(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        enter_name = cst.Name(value="_enter_ctrl_flow_")
        enter_arg = cst.Arg(value=updated_node.test)
        enter_call = cst.Call(func=enter_name, args=[iid_arg, enter_arg])
        end_name = cst.Name(value="_exit_ctrl_flow_")
        end_call = cst.Call(func=end_name, args=[iid_arg])
        else_part = cst.Else(body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=end_call)])]))
        return updated_node.with_changes(test=enter_call, orelse=else_part)
    
    def leave_IndentedBlock(self, original_node, updated_node):
        if 'control_flow' not in self.selected_hooks:
            return updated_node
        new_body = []
        for i in updated_node.body:
            if matchers.matches(i, matchers.SimpleStatementLine(body=[matchers.Break()])):
                callee_name = cst.Name(value="_jump_")
                iid = self.__create_iid(original_node)
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                break_arg = cst.Arg(value=cst.Name(value='True'))
                call = cst.Call(func=callee_name, args=[iid_arg, break_arg])
                condition = cst.If(test=call, body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Break()])]))
                new_body.append(condition)
            elif matchers.matches(i, matchers.SimpleStatementLine(body=[matchers.Continue()])):
                callee_name = cst.Name(value="_jump_")
                iid = self.__create_iid(original_node)
                iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
                break_arg = cst.Arg(value=cst.Name(value='False'))
                call = cst.Call(func=callee_name, args=[iid_arg, break_arg])
                condition = cst.If(test=call, body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Continue()])]))
                new_body.append(condition)
            else:
                new_body.append(i)

        return updated_node.with_changes(body=new_body)
        