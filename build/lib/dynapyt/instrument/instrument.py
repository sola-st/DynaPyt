import argparse
import importlib
import libcst as cst
from .CodeInstrumenter import CodeInstrumenter
from .IIDs import IIDs
import re
from shutil import copyfile


parser = argparse.ArgumentParser()
parser.add_argument(
    "--files", help="Python files to instrument or .txt file with all file paths", nargs="+")
parser.add_argument(
    "--iids", help="JSON file with instruction IDs (will create iids.json if nothing given)")
parser.add_argument(
    "--analysis", help="Analysis class name")

def get_hooks_from_analysis(method_list):
    print(method_list)
    return ['read', 'literal', 'call', 'unary_operation', 'binary_operation']

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


def instrument_file(file_path, iids, selected_hooks):
    with open(file_path, 'r') as file:
        src = file.read()

    if 'DYNAPYT: DO NOT INSTRUMENT' in src:
        print(f'{file_path} is already instrumented -- skipping it')
        return

    ast = cst.parse_module(src)
    ast_wrapper = cst.metadata.MetadataWrapper(ast)

    instrumented_code = CodeInstrumenter(src, file_path, iids, selected_hooks)
    instrumented_ast = ast_wrapper.visit(instrumented_code)

    copied_file_path = re.sub(r'\.py$', '.py.orig', file_path)
    copyfile(file_path, copied_file_path)

    rewritten_code = '# DYNAPYT: DO NOT INSTRUMENT\n\n' + instrumented_ast.code
    with open(file_path, 'w') as file:
        file.write(rewritten_code)
    print(f'Done with {file_path}')


if __name__ == '__main__':
    args = parser.parse_args()
    files = gather_files(args.files)
    iids = IIDs(args.iids)
    
    module = importlib.import_module('dynapyt.analyses.' + args.analysis)
    print(module)
    class_ = getattr(module, args.analysis)
    instance = class_()
    method_list = [func for func in dir(instance) if callable(getattr(instance, func)) and not func.startswith("__")]
    selected_hooks = get_hooks_from_analysis(method_list)
    for file_path in files:
        instrument_file(file_path, iids, selected_hooks)
    iids.store()
