from importlib import import_module
from os import sep, remove
from os.path import join, exists
from pathlib import Path
from shutil import copyfile, move
from inspect import getmembers, isclass
from typing import Tuple
import json
import pytest

from dynapyt.instrument.instrument import instrument_file
from dynapyt.utils.hooks import get_hooks_from_analysis
from dynapyt.run_analysis import run_analysis
import dynapyt.runtime as rt
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


def correct_output(expected: str, actual: str) -> bool:
    if actual == expected or actual == expected + "\n":
        return True
    actual_lines = actual.strip().split("\n")
    expected_lines = expected.strip().split("\n")
    if len(actual_lines) != len(expected_lines):
        return False
    for i in range(len(actual_lines)):
        if "<...>" in expected_lines[i]:
            pre_ex, post_ex = expected_lines[i].split("<...>")
            if not (
                actual_lines[i].startswith(pre_ex) and actual_lines[i].endswith(post_ex)
            ):
                return False
        elif actual_lines[i] != expected_lines[i]:
            return False
    return True


def correct_coverage(expected: str, actual: str) -> bool:
    actual_lines = actual.strip().split("\n")
    expected_lines = expected.strip().split("\n")
    if len(actual_lines) != len(expected_lines):
        return False
    for i in range(len(actual_lines)):
        actual_line = json.loads(actual_lines[i].replace("\\\\", "/"))
        expected_line = json.loads(expected_lines[i])
        for f, cov in actual_line.items():
            file_path = f.split("/tests/")[1]
            if file_path not in expected_line:
                return False
            for l in cov:
                if l not in expected_line[file_path]:
                    return False
                if expected_line[file_path][l] != cov[l]:
                    return False
    return True


def test_runner(directory_pair: Tuple[str, str], capsys):
    abs_dir, rel_dir = directory_pair

    # gather hooks used by the analysis
    module_prefix = rel_dir.replace(sep, ".")
    module = import_module(f"{module_prefix}.analysis")
    analysis_classes = getmembers(
        module, lambda c: isclass(c) and issubclass(c, BaseAnalysis)
    )
    selected_hooks = get_hooks_from_analysis(
        [f"{module_prefix}.analysis.{ac[0]}" for ac in analysis_classes]
    )

    if (Path(abs_dir) / "exp_coverage.jsonl").exists():
        cov = True
        coverage_dir = str(abs_dir)
    else:
        cov = False
        coverage_dir = None

    # instrument
    program_file = str(Path(abs_dir) / "program.py")
    orig_program_file = str(Path(abs_dir) / "program.py.orig")
    # make sure to instrument the uninstrumented version
    run_as_file = False
    with open(program_file, "r") as file:
        src = file.read()
        if "DYNAPYT: DO NOT INSTRUMENT" in src:
            if not exists(orig_program_file):
                pytest.fail(f"Could find only the instrumented program in {rel_dir}")
            copyfile(orig_program_file, program_file)
        elif "# DYNAPYT: Run as file" in src:
            run_as_file = True

    instrument_file(program_file, selected_hooks)

    if exists(join(abs_dir, "__init__.py")) and not exists(
        join(abs_dir, "__init__.py.orig")
    ):
        instrument_file(join(abs_dir, "__init__.py"), selected_hooks)

    # analyze
    captured = capsys.readouterr()  # clear stdout
    # print(f"Before analysis: {captured.out}")  # for debugging purposes
    if run_as_file:
        run_analysis(
            program_file,
            [f"{module_prefix}.analysis.TestAnalysis"],
            coverage=cov,
            coverage_dir=coverage_dir,
        )
    else:
        run_analysis(
            f"{module_prefix}.program",
            [
                f"{module_prefix}.analysis.{ac[0]}"
                for ac in analysis_classes
                if not ac[0].endswith("BaseAnalysis")
            ],
            coverage=cov,
            coverage_dir=coverage_dir,
        )

    # check output
    expected_file = join(abs_dir, "expected.txt")
    with open(expected_file, "r") as file:
        expected = file.read()

    captured = (
        capsys.readouterr()
    )  # read stdout produced by running the analyzed program
    if not correct_output(expected, captured.out):
        pytest.fail(
            f"Output of {rel_dir} does not match expected output.\n--> Expected:\n{expected}\n--> Actual:\n{captured.out}"
        )

    expected_coverage = join(abs_dir, "exp_coverage.jsonl")
    if exists(expected_coverage):
        with open(expected_coverage, "r") as file:
            expected = file.read()
        with open(join(coverage_dir, "covered.jsonl"), "r") as file:
            actual = file.read()
        if not correct_coverage(expected, actual):
            pytest.fail(
                f"Coverage of {rel_dir} does not match expected coverage.\n--> Expected:\n{expected}\n--> Actual:\n{actual}"
            )

    # restore uninstrumented program and remove temporary files
    move(orig_program_file, program_file)
    remove(join(abs_dir, "program-dynapyt.json"))
    if cov:
        remove(join(abs_dir, "covered.jsonl"))
        remove(join(abs_dir, "covered.jsonl.lock"))
    if exists(join(abs_dir, "__init__.py")) and exists(
        join(abs_dir, "__init__.py.orig")
    ):
        move(join(abs_dir, "__init__.py.orig"), join(abs_dir, "__init__.py"))
        remove(join(abs_dir, "__init__-dynapyt.json"))
