import argparse
from os import path
import libcst as cst
import re
from shutil import copyfile

import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider


parser = argparse.ArgumentParser()
parser.add_argument(
    "--files", help="Python files to instrument or .txt file with all file paths", nargs="+")
parser.add_argument(
    "--mod", help="Trace mode, can be \'opcode\', \'assignment\', or \'all\'", nargs=1)


class CodeInstrumenter(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider,)
    def __init__(self, mod):
        if 'opcode' in mod:
            self.hook = '_trace_opcodes_'
        elif 'assignment' in mod:
            self.hook = '_trace_assignments_'
        else:
            self.hook = '_trace_all_'

    def __create_import(self, name):
        # module_name = cst.Attribute(value=cst.Name(value=cst.Name(cst.Attribute(value=cst.Name("dynapyt")), attr=cst.Name("evaluation"))), attr=cst.Name(value="instrument_tracer"))
        module_name = cst.Attribute(value=cst.Name('nativetracer'), attr=cst.Name('trc'))
        fct_name = cst.Name(value=name)
        imp_alias = cst.ImportAlias(name=fct_name)
        imp = cst.ImportFrom(module=module_name, names=[imp_alias])
        stmt = cst.SimpleStatementLine(body=[imp])
        return stmt

    def leave_Module(self, original_node, updated_node):
        import_assign = self.__create_import(self.hook)
        callee = cst.Name(value='settrace')
        arg = cst.Arg(cst.Name(value=self.hook))
        call_trc = cst.Call(func=callee, args=[arg])

        module_name = value=cst.Name('sys')
        fct_name = cst.Name(value='settrace')
        imp_alias = cst.ImportAlias(name=fct_name)
        imp = cst.ImportFrom(module=module_name, names=[imp_alias])
        stmt = cst.SimpleStatementLine(body=[imp])

        func = cst.FunctionDef(name=cst.Name('_native_tracer_run_'), params=cst.Parameters(params=[]), body=cst.IndentedBlock(body=updated_node.body))
        func_call = cst.SimpleStatementLine(body=[cst.Expr(cst.Call(func=cst.Name('_native_tracer_run_'), args=[]))])

        new_body = [import_assign, stmt, cst.Newline(value='\n'), func, cst.SimpleStatementLine(body=[cst.Expr(call_trc)]), func_call]
        return updated_node.with_changes(body=new_body)

def gather_files(files_arg):
    if len(files_arg) == 1 and files_arg[0].endswith('.txt'):
        files = []
        with open(files_arg[0]) as fp:
            for line in fp.readlines():
                files.append(line.rstrip())
    else:
        for f in files_arg:
            if not f.endswith('.py'):
                raise Exception(f'Incorrect argument, expected .py file: {f}')
        files = files_arg
    return files


def instrument_file(file_path, mod):
    with open(file_path, 'r') as file:
        src = file.read()

    if 'tracer: DO NOT INSTRUMENT' in src:
        print(f'{file_path} is already instrumented -- skipping it')
        return

    ast = cst.parse_module(src)
    ast_wrapper = cst.metadata.MetadataWrapper(ast)

    instrumented_code = CodeInstrumenter(mod)
    instrumented_ast = ast_wrapper.visit(instrumented_code)
    # print(instrumented_ast)

    copied_file_path = re.sub(r'\.py$', '.py.orig', file_path)
    copyfile(file_path, copied_file_path)

    rewritten_code = '# tracer: DO NOT INSTRUMENT\n\n' + instrumented_ast.code
    with open(file_path, 'w') as file:
        file.write(rewritten_code)


if __name__ == '__main__':
    args = parser.parse_args()
    files = gather_files(args.files)
    for file_path in files:
        instrument_file(file_path, args.mod)
