from importlib import import_module
from os import sep, remove
from os.path import join, exists
from shutil import copyfile, move
from typing import Tuple
import pytest

from dynapyt.instrument.instrument import instrument_file
from dynapyt.utils.hooks import get_hooks_from_analysis
import dynapyt.runtime as rt


def test_runner(directory_pair: Tuple[str, str], capsys):
    abs_dir, rel_dir = directory_pair

    # gather hooks used by the analysis
    module_prefix = rel_dir.replace(sep, ".")
    module = import_module(f"{module_prefix}.analysis")
    class_ = getattr(module, "TestAnalysis")
    analysis_instance = class_()
    method_list = [
        func
        for func in dir(analysis_instance)
        if callable(getattr(analysis_instance, func)) and not func.startswith("__")
    ]
    selected_hooks = get_hooks_from_analysis(set(method_list))

    # instrument
    program_file = join(abs_dir, "program.py")
    orig_program_file = join(abs_dir, "program.py.orig")
    # make sure to instrument the uninstrumented version
    with open(program_file, "r") as file:
        src = file.read()
        if "DYNAPYT: DO NOT INSTRUMENT" in src:
            if not exists(orig_program_file):
                pytest.fail(f"Could find only the instrumented program in {rel_dir}")
            copyfile(orig_program_file, program_file)

    instrument_file(program_file, selected_hooks)

    # analyze
    rt.set_analysis(analysis_instance)
    captured = capsys.readouterr()  # clear stdout
    if hasattr(analysis_instance, "begin_execution"):
        analysis_instance.begin_execution()
    import_module(f"{module_prefix}.program")
    if hasattr(analysis_instance, "end_execution"):
        analysis_instance.end_execution()

    # check output
    expected_file = join(abs_dir, "expected.txt")
    with open(expected_file, "r") as file:
        expected = file.read()

    captured = (
        capsys.readouterr()
    )  # read stdout produced by running the analyzed program
    if captured.out != expected and captured.out != expected + "\n":
        pytest.fail(
            f"Output of {rel_dir} does not match expected output.\n--> Expected:\n{expected}\n--> Actual:\n{captured.out}"
        )

    # restore uninstrumented program and remove temporary files
    move(orig_program_file, program_file)
    remove(join(abs_dir, "program-dynapyt.json"))
