from importlib import import_module
from os import sep, remove, environ
from os.path import join, exists
from pathlib import Path
from shutil import copyfile, move, rmtree
from tempfile import gettempdir
from inspect import getmembers, isclass
from typing import Tuple
import json
import pytest

from dynapyt.instrument.instrument import instrument_file
from dynapyt.utils.hooks import get_hooks_from_analysis
from dynapyt.run_analysis import run_analysis
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.utils.runtimeUtils import gather_coverage


def correct_output(
    expected: str, actual: str, exception: Exception
) -> tuple[bool, int]:
    if exception:
        actual += f"# Exception: {str(exception)}"
    actual = actual.strip()
    expected = expected.strip()
    if actual == expected:
        return True, 0
    actual_lines = [l.strip() for l in actual.strip().split("\n")]
    expected_lines = [l.strip() for l in expected.strip().split("\n")]
    if len(actual_lines) != len(expected_lines):
        return False, -1
    for i in range(len(actual_lines)):
        if "<...>" in expected_lines[i]:
            pre_ex, post_ex = expected_lines[i].split("<...>")
            if not (
                actual_lines[i].startswith(pre_ex) and actual_lines[i].endswith(post_ex)
            ):
                return False, i
        elif actual_lines[i] != expected_lines[i]:
            return False, i
    return True, 0


def correct_coverage(expected: str, actual: str) -> bool:
    actual_cov = {
        k.replace("\\", "/").replace("//", "/").split("/tests/")[1]: v
        for k, v in json.loads(actual).items()
    }
    expected_cov = json.loads(expected)
    return actual_cov == expected_cov


def test_runner(directory_pair: Tuple[str, str], capsys):
    abs_dir, rel_dir = directory_pair
    if (Path(abs_dir) / "skip.txt").exists():
        pytest.skip(f"Skipping test {rel_dir}")

    exception = None

    # gather hooks used by the analysis
    module_prefix = rel_dir.replace(sep, ".")
    module = import_module(f"{module_prefix}.analysis")
    analysis_classes = getmembers(
        module, lambda c: isclass(c) and issubclass(c, BaseAnalysis)
    )
    selected_hooks = get_hooks_from_analysis(
        [f"{module_prefix}.analysis.{ac[0]}" for ac in analysis_classes]
    )

    if (Path(abs_dir) / "exp_coverage.json").exists():
        cov = True
        coverage_dir = str(abs_dir)
    else:
        cov = False
        coverage_dir = None

    # instrument
    program_files = [str(f) for f in Path(abs_dir).glob("program*.py")]
    for program_file in program_files:
        # program_file = str(Path(abs_dir) / "program.py")
        orig_program_file = program_file + ".orig"
        # make sure to instrument the uninstrumented version
        run_as_file = False
        with open(program_file, "r") as file:
            src = file.read()
            if "DYNAPYT: DO NOT INSTRUMENT" in src:
                if not exists(orig_program_file):
                    pytest.fail(
                        f"Could find only the instrumented program in {rel_dir}"
                    )
                copyfile(orig_program_file, program_file)
            elif "# DYNAPYT: Run as file" in src:
                run_as_file = True

        ret_value = instrument_file(program_file, selected_hooks)

    if exists(join(abs_dir, "__init__.py")) and not exists(
        join(abs_dir, "__init__.py.orig")
    ):
        ret_value = instrument_file(join(abs_dir, "__init__.py"), selected_hooks)

    if ret_value is not None and ret_value != 0:
        pytest.fail(f"Error while instrumenting {rel_dir}")

    # analyze
    captured = capsys.readouterr()  # clear stdout
    # print(f"Before analysis: {captured.out}")  # for debugging purposes

    try:
        if run_as_file:
            session_id = run_analysis(
                program_file,
                [f"{module_prefix}.analysis.TestAnalysis"],
                coverage=cov,
                coverage_dir=coverage_dir,
            )
        else:
            session_id = run_analysis(
                f"{module_prefix}.program",
                [
                    f"{module_prefix}.analysis.{ac[0]}"
                    for ac in analysis_classes
                    if not ac[0].endswith("BaseAnalysis")
                ],
                coverage=cov,
                coverage_dir=coverage_dir,
            )
    except Exception as e:
        exception = e
        session_id = environ.get("DYNAPYT_SESSION_ID", None)

    # check output
    expected_file = join(abs_dir, "expected.txt")
    with open(expected_file, "r") as file:
        expected = file.read()

    captured = (
        capsys.readouterr()
    )  # read stdout produced by running the analyzed program
    actual = captured.out
    output_res = correct_output(expected, actual, exception)
    if not output_res[0]:
        pytest.fail(
            f"Output of {rel_dir} does not match expected output on line {output_res[1]}.\n--> Expected:\n{expected}\n--> Actual:\n{actual}\n--> Exception: {exception}"
        )

    expected_coverage = join(abs_dir, "exp_coverage.json")
    if exists(expected_coverage):
        with open(expected_coverage, "r") as file:
            expected = file.read()
        gather_coverage(Path(coverage_dir) / f"dynapyt_coverage-{session_id}")
        with open(
            join(coverage_dir, f"dynapyt_coverage-{session_id}", "coverage.json"), "r"
        ) as file:
            actual = file.read()
        if not correct_coverage(expected, actual):
            pytest.fail(
                f"Coverage of {rel_dir} does not match expected coverage.\n--> Expected:\n{expected}\n--> Actual:\n{actual}"
            )

    # restore uninstrumented program and remove temporary files
    try:
        for program_file in program_files:
            orig_program_file = program_file + ".orig"
            move(orig_program_file, program_file)
            remove(join(abs_dir, f"{program_file[:-3]}-dynapyt.json"))
        if cov:
            cov_dirs = Path(coverage_dir).glob("dynapyt_coverage-*")
            for cov_dir in cov_dirs:
                rmtree(coverage_dir / cov_dir)
        if exists(join(abs_dir, "__init__.py")) and exists(
            join(abs_dir, "__init__.py.orig")
        ):
            move(join(abs_dir, "__init__.py.orig"), join(abs_dir, "__init__.py"))
            remove(join(abs_dir, "__init__-dynapyt.json"))
        if (Path(gettempdir()) / f"dynapyt_analyses-{session_id}.txt").exists():
            (Path(gettempdir()) / f"dynapyt_analyses-{session_id}.txt").unlink()
        if (Path(gettempdir()) / f"dynapyt_output-{session_id}").exists():
            rmtree(Path(gettempdir()) / f"dynapyt_output-{session_id}")
    except FileNotFoundError as fe:
        raise FileNotFoundError(f"File not found {fe} in {rel_dir}")
    except Exception as e:
        raise Exception(f"Something went wrong while cleaning up {rel_dir}: {e}")
