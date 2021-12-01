import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider
import libcst.matchers as matchers
import libcst.helpers as helpers


class CodeInstrumenter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider,)

    def __init__(self, file_path, iids, selected_hooks):
        self.file_path = file_path
        self.iids = iids
        self.name_stack = []
        self.selected_hooks = selected_hooks

    def __create_iid(self, node):
        location = self.get_metadata(PositionProvider, node)
        line = location.start.line
        column = location.start.column
        iid = self.iids.new(self.file_path, line, column)
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

    # add import of our runtime library to the file
    def leave_Module(self, original_node, updated_node):
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
        dynapyt_imports.append(cst.Newline(value='\n'))
        new_body = list(updated_node.body[:imports_index+1]) + dynapyt_imports + list(updated_node.body[imports_index+1:])
        return updated_node.with_changes(body=new_body)

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
        val_arg = cst.Arg(self.__wrap_in_lambda(original_node))
        call = cst.Call(func=callee_name, args=[
                        iid_arg, left_arg, operator_arg, right_arg, val_arg])
        return call
    
    def leave_Assign(self, original_node, updated_node):
        if 'assignment' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_assign_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        left_arg = cst.Arg(value=cst.SimpleString('\"' + cst.Module([]).code_for_node(updated_node) + '\"'))
        right_arg = cst.Arg(value=self.__wrap_in_lambda(updated_node))
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
        call = cst.Call(func=callee_name, args=[iid_arg])
        return call
    
    def leave_Call(self, original_node, updated_node):
        if 'call' not in self.selected_hooks:
            return updated_node
        callee_name = cst.Name(value="_call_")
        iid = self.__create_iid(original_node)
        iid_arg = cst.Arg(value=cst.Integer(value=str(iid)))
        call_arg = cst.Arg(value=self.__wrap_in_lambda(updated_node))
        call = cst.Call(func=callee_name, args=[iid_arg, call_arg])
        return call
        