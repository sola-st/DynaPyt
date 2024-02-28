import fire
import json
from pathlib import Path
from shutil import rmtree
from inspect import getmembers, isclass
from importlib import import_module, invalidate_caches
from tempfile import gettempdir
from dynapyt.instrument.instrument import instrument_file
from dynapyt.run_analysis import run_analysis
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.utils.hooks import get_hooks_from_analysis


def match_output(actual: list[list], expected: list[list]) -> bool:
    if len(actual) != len(expected):
        return False
    for i in range(len(actual)):
        found = False
        for j in range(len(expected)):
            if "\n".join(actual[i]) == "\n".join(expected[j]):
                found = True
                break
        if not found:
            return False
    return True


def run_project(project_path: str, module_name: str, path_to_tests: str):
    print(f"Running project {project_path}")

    # Instrument all Python files in the project
    module = import_module(f"{module_name}.analysis")
    analysis_classes = getmembers(
        module,
        lambda c: isclass(c) and issubclass(c, BaseAnalysis) and c != BaseAnalysis,
    )
    selected_hooks = get_hooks_from_analysis(
        [f"{module_name}.analysis.{ac[0]}" for ac in analysis_classes]
    )
    here = Path(__file__).parent
    project_dir = (here / ".." / "projects" / project_path).resolve()
    for code_file in project_dir.rglob("*.py"):
        instrument_file(str(project_dir / code_file), selected_hooks)

    # Run the analysis by running the tests
    test_code = f"import pytest\npytest.main(['-n', 'auto', '--dist', 'worksteal', '--import-mode=importlib', '{str(project_dir/path_to_tests)}'])"
    cov_dir = Path(gettempdir()) / "dynapyt_coverage"
    cov_dir.mkdir(exist_ok=True)
    session_id = run_analysis(
        entry=f"{module_name}.src.{module_name}.main",
        analyses=[f"{module_name}.analysis.{ac[0]}" for ac in analysis_classes],
        output_dir=str(project_dir),
        coverage=True,
        coverage_dir=cov_dir,
        script=test_code,
    )

    # Check if the output matches the expected output
    output_file = Path(project_dir) / f"dynapyt_output-{session_id}" / "output.json"
    expected_output = Path(project_dir) / "expected_output.json"
    with open(output_file, "r") as f:
        actual = json.load(f)
    with open(expected_output, "r") as f:
        expected = json.load(f)
    if not match_output(actual, expected):
        failed = f"Output does not match expected output: {actual} != {expected}"
    output_file.unlink()

    # Check if the coverage matches the expected coverage
    coverage_file = cov_dir / f"dynapyt_coverage-{session_id}" / "coverage.json"
    expected_coverage = project_dir / "expected_coverage.json"
    with open(coverage_file, "r") as f:
        actual = json.load(f)
    with open(expected_coverage, "r") as f:
        expected = json.load(f)
    if actual != expected:
        failed = f"Coverage does not match expected coverage: {actual} != {expected}"
    coverage_file.unlink()

    # Clean up the project
    for code_file in project_dir.rglob("*.py.orig"):
        metadata_file = (
            project_dir
            / Path(*(code_file.parts[:-1]))
            / (code_file.name[:-8] + "-dynapyt.json")
        )
        metadata_file.unlink()
        correct_file = (
            project_dir / Path(*(code_file.parts[:-1])) / (code_file.name[:-8] + ".py")
        )
        code_file.rename(correct_file)
    rmtree(cov_dir)
    if failed:
        raise ValueError(failed)


if __name__ == "__main__":
    fire.Fire(run_project)
