import argparse
from multiprocessing import Pool
import traceback
import libcst as cst
from libcst._exceptions import ParserSyntaxError
from .CodeInstrumenter import CodeInstrumenter
from .IIDs import IIDs
import re
from shutil import copyfile
from dynapyt.utils.hooks import get_hooks_from_analysis


def gather_files(files_arg):
    if len(files_arg) == 1 and files_arg[0].endswith(".txt"):
        files = []
        with open(files_arg[0]) as fp:
            for line in fp.readlines():
                files.append(line.rstrip())
    else:
        for f in files_arg:
            if not f.endswith(".py"):
                raise Exception(f"Incorrect argument, expected .py file: {f}")
        files = files_arg
    return files


def canonical_ifs(node, child_dict):
    new_body = (
        cst.Break()
        if cst.matchers.matches(node.body.body[0], cst.matchers.Break())
        else cst.Continue()
    )
    return cst.If(
        test=node.test,
        body=cst.IndentedBlock(body=[cst.SimpleStatementLine(body=[new_body])]),
        orelse=node.orelse,
        leading_lines=node.leading_lines,
        whitespace_before_test=node.whitespace_before_test,
        whitespace_after_test=node.whitespace_after_test,
    )


def instrument_code(src, file_path, iids, selected_hooks):
    try:
        ast = cst.matchers.replace(
            cst.parse_module(src),
            cst.matchers.If(
                body=cst.matchers.SimpleStatementSuite(
                    body=[(cst.matchers.Break() | cst.matchers.Continue())]
                )
            ),
            canonical_ifs,
        )
        ast_wrapper = cst.metadata.MetadataWrapper(ast)

        instrumented_code = CodeInstrumenter(src, file_path, iids, selected_hooks)
        instrumented_ast = ast_wrapper.visit(instrumented_code)

        return "# DYNAPYT: DO NOT INSTRUMENT\n\n" + instrumented_ast.code
    except ParserSyntaxError:
        print(f"Syntax error in {file_path} -- skipping it")
        return None
    except Exception as e:
        print(f"Error in {file_path} -- skipping it")
        print(e)
        print(traceback.format_exc())
        return None


def instrument_file(file_path, selected_hooks):
    try:
        with open(file_path, "r") as file:
            src = file.read()
    except (UnicodeDecodeError, ValueError):
        print(f"Error reading {file_path} -- skipping it")
        return 1
    if "DYNAPYT: DO NOT INSTRUMENT" in src:
        print(f"{file_path} is already instrumented -- skipping it")
        return 0
    iids = IIDs(file_path)

    instrumented_code = instrument_code(src, file_path, iids, selected_hooks)
    if instrumented_code is None:
        return 1

    copied_file_path = re.sub(r"\.py$", ".py.orig", file_path)
    copyfile(file_path, copied_file_path)

    with open(file_path, "w") as file:
        file.write(instrumented_code)
    iids.store()
    print(f"Done with {file_path}")


def instrument_files(files, analyses):
    selected_hooks = get_hooks_from_analysis(analyses)
    if len(files) < 2:
        for file_path in files:
            instrument_file(file_path, selected_hooks)
    else:
        arg_list = []
        for file_path in files:
            arg_list.append((file_path, selected_hooks))
        with Pool(maxtasksperchild=5) as p:
            p.starmap(instrument_file, arg_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--files",
        help="Python files to instrument or .txt file with all file paths",
        nargs="+",
        required=True,
    )
    parser.add_argument(
        "--analysis",
        help="Analysis class(es) (full dotted path)",
        nargs="+",
        required=True,
    )
    args = parser.parse_args()
    files = gather_files(args.files)
    instrument_files(files, args.analysis)
