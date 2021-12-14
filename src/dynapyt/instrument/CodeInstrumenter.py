import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider
import libcst.matchers as matchers
import libcst.helpers as helpers
from libcst.metadata.expression_context_provider import ExpressionContext


class CodeInstrumenter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider, ScopeProvider, ExpressionContextProvider,)

    def __init__(self, src, file_path, iids, selected_hooks):
        self.source = src
        self.file_path = file_path
        self.iids = iids
        self.name_stack = []
        self.selected_hooks = selected_hooks

    def __create_iid(self, node):
        location = self.get_metadata(PositionProvider, node)
        line = location.start.line
        column = location.start.column
        iid = self.iids.new(self.file_path, line, column, node)
        return iid

    def __create_import(self, name):
        module_name = cst.Attribute(value= cst.Name(value='dynapyt'), attr=cst.Name(value="runtime"))
        fct_name = cst.Name(value=name)
        imp_alias = cst.ImportAlias(name=fct_name)
        imp = cst.ImportFrom(module=module_name, names=[imp_alias])
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt
    
    def __wrap_in_lambda(self, node):
        used_names = set(map(lambda x: x.value, matchers.findall(node, matchers.Name())))
        parameters = []
        for n in used_names:
            parameters.append(cst.Param(name=cst.Name(value=n), default=cst.Name(value=n)))
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
        dynapyt_imports.append(self.__create_import("_dynapyt_parse_to_ast_"))
        dynapyt_imports.append(self.__create_import("_catch_"))
        if 'assignment' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_assign_"))
        if 'expression' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_expr_"))
        if 'binary_operation' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_binary_op_"))
        if 'unary_operation' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_unary_op_"))
        if 'call' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_call_"))
        if 'literal' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_literal_"))
        if 'exception' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_raise_"))
        if 'read' in self.selected_hooks:
            dynapyt_imports.append(self.__create_import("_read_var_"))
        dynapyt_imports.append(cst.Newline(value='\n'))
        code_body = list(updated_node.body[imports_index+1:])
        handler_call = cst.Call(func=cst.Name(value='_catch_'), args=[cst.Arg(cst.Name('_dynapyt_exception_'))])
        handler_body = cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[cst.Expr(value=handler_call)])])
        try_body = cst.Try(body=cst.IndentedBlock(body=code_body), handlers=[cst.ExceptHandler(body=handler_body, type=cst.Name(value='Exception'), name=cst.AsName(cst.Name(value='_dynapyt_exception_')))])
        new_body = list(updated_node.body[:imports_index+1]) + dynapyt_imports + [source_code, get_ast] + [try_body]
        return updated_node.with_changes(body=new_body)

    def leave_Name(self, original_node, updated_node):
        if 'read' not in self.selected_hooks:
            return updated_node
        context = self.get_metadata(ExpressionContextProvider, original_node)
        print(original_node, context, context == ExpressionContext.LOAD)
        if context == ExpressionContext.LOAD:
            callee_name = cst.Name(value="_read_var_")
            iid = self.__create_iid(original_node)
            iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
            var_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
            call = cst.Call(func=callee_name, args=[iid_arg, var_arg])
            return call
        else:
            return updated_node

    def leave_BinaryOperation(self, original_node, updated_node):
        if 'binary_operation' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_binary_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(updated_node.left)
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.SimpleString(value=f'"{operator_name}"'))
        right_arg = cst.Arg(updated_node.right)
        call = cst.Call(func=callee_name, args=[
                        iid_arg, left_arg, operator_arg, right_arg])
        return call
    
    def leave_Assign(self, original_node, updated_node):
        if 'assignment' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_assign_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(value=cst.SimpleString('\"' + cst.Module([]).code_for_node(updated_node) + '\"'))
        right_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[iid_arg, left_arg, right_arg])
        new_node = cst.SimpleStatementLine(body=[cst.Expr(value=call)])
        print(new_node)
        return new_node
    
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
        if 'function_def' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_func_entry_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        entry_stmt = cst.Expr(cst.Call(func=callee_name, args=[iid_arg]))
        new_body = updated_node.body.with_changes(body=[cst.SimpleStatementLine([entry_stmt])]+list(updated_node.body.body))
        new_node = updated_node
        return new_node.with_changes(body=new_body)
    
    def leave_UnaryOperation(self, original_node, updated_node):
        if 'unary_operation' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_unary_op_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        operator_name = type(original_node.operator).__name__
        operator_arg = cst.Arg(cst.SimpleString(value=f'"{operator_name}"'))
        right_arg = cst.Arg(updated_node.expression)
        val_arg = cst.Arg(self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[
                        iid_arg, operator_arg, right_arg, val_arg])
        return call
    
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
    
    def leave_Raise(self, original_node, updated_node):
        if 'exception' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_raise_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        raise_arg = cst.Arg(value=self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[iid_arg, raise_arg])
        return call
        