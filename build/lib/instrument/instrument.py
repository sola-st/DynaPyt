import argparse
from os import path
import libcst as cst
from CodeInstrumenter import CodeInstrumenter
from IIDs import IIDs
import re
from shutil import copyfile


parser = argparse.ArgumentParser()
parser.add_argument(
    "--files", help="Python files to instrument or .txt file with all file paths", nargs="+")
parser.add_argument(
    "--iids", help="JSON file with instruction IDs (will create iids.json if nothing given)")


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


def instrument_file(file_path, iids):
    with open(file_path, 'r') as file:
        src = file.read()

    if 'DYNAPYT: DO NOT INSTRUMENT' in src:
        print(f'{file_path} is already instrumented -- skipping it')
        return

    ast = cst.parse_module(src)
    ast_wrapper = cst.metadata.MetadataWrapper(ast)

    instrumented_code = CodeInstrumenter(file_path, iids)
    instrumented_ast = ast_wrapper.visit(instrumented_code)
    # print(instrumented_ast)

    copied_file_path = re.sub(r'\.py$', '.py.orig', file_path)
    copyfile(file_path, copied_file_path)

    rewritten_code = '# DYNAPYT: DO NOT INSTRUMENT\n\n' + instrumented_ast.code
    with open(file_path, 'w') as file:
        file.write(rewritten_code)


if __name__ == '__main__':
    args = parser.parse_args()
    files = gather_files(args.files)
    iids = IIDs(args.iids)
    for file_path in files:
        instrument_file(file_path, iids)
    iids.store()
