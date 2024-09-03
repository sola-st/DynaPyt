import json
from pathlib import Path
import pytest
from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from dynapyt.instrument.instrument import instrument_file
from dynapyt.utils.hooks import get_hooks_from_analysis
import subprocess
import sys


def run_project(project: Path):
    project_dir = project.resolve()
    json_report_file = project_dir / "result.json"
    result = pytest.main(["-v", "--cache-clear", "--json-report", "--json-report-file="+str(json_report_file), str(project_dir/"tests"), ])
    with open(json_report_file, "r") as f:
        result = f.read()

    result_json = json.loads(result)
    test_result_map = {}
    for item in result_json["tests"]:
        test_result_map[item["nodeid"]] = item["outcome"]
    json_report_file.unlink()
    return test_result_map


def run_instrumented_project(project):
    selected_hooks = get_hooks_from_analysis(["analysis.analysis.Analysis"])
    project_dir = project.resolve()
    project_src_dir = project_dir / "src"
    for code_file in project_src_dir.rglob("*.py"):
        instrument_file(str(project_dir / code_file), selected_hooks)

    install_project(project)
    json_report_file = project_dir / "instrumented_result.json"
    result = pytest.main(["-v", "--cache-clear", "--json-report", "--json-report-file="+str(json_report_file), str(project_dir/"tests"), ])
    with open(json_report_file, "r") as f:
        result = f.read()
    
    result_json = json.loads(result)
    test_result_map = {}
    for item in result_json["tests"]:
        test_result_map[item["nodeid"]] = item["outcome"]

    # Clean up the project
    for code_file in project_dir.rglob("*.py.orig"):
            metadata_file = (
                project_dir
                / Path(*(code_file.parts[:-1]))
                / (code_file.name[:-8] + "-dynapyt.json")
            )
            metadata_file.unlink()
            correct_file = (
                project_dir
                / Path(*(code_file.parts[:-1]))
                / (code_file.name[:-8] + ".py")
            )
            code_file.rename(correct_file)
    json_report_file.unlink()

    return test_result_map


def remove_related_modules(project):
    project_module = project.name.replace("-", "_")

    project_src_dir = project / "src"
    for code_file in project_src_dir.rglob("*.py"): 
        module_name = project_module + "." + code_file.stem
        if module_name in sys.modules:
            print(f"Deleting module {module_name}")
            del sys.modules[module_name]

    project_test_dir = project / "tests"
    for code_file in project_test_dir.rglob("*.py"):
        module_name = code_file.stem
        if module_name in sys.modules:
            print(f"Deleting module {module_name}")
            del sys.modules[module_name]


def run_tests(projects_dir):
    invariance_test_node_id = "tests/stack_test.py::test_stack"
    failed = False
    # Run the tests with and without instrumentation
    for project in projects_dir.iterdir():
        print(f"Installing project {project.name}")
        install_project(project)
        print(f"Running project {project.name}")
        test_result = run_project(project)
        remove_related_modules(project)
        instrumented_test_result = run_instrumented_project(project)

        for test, result in test_result.items():
            if (test not in instrumented_test_result):
                print(f"Test {test} not found in instrumented test results")
                failed = True
                break
            if test == invariance_test_node_id:
                if (result == instrumented_test_result[test]):
                    print(f"Test {test} results match for invariance test")
                    failed = True
                    break
                else:
                    continue
            if (result != instrumented_test_result[test]):
                print(f"Test {test} results do not match")
                failed = True
                break
        sys.path.remove(str(project / "src"))
        sys.path.remove(str(project.parent))

    if failed:
        print("Test results do not match before and after instrumentation")
        return False
    
    print(f"All tests passed for projects in folder {projects_dir}")

    return True


def install_project(projects_dir):
    subprocess.run(["pip", "install", "-e", str(projects_dir)])
    requirements_file = projects_dir / "requirements.txt"
    if requirements_file.exists():
        subprocess.run(["pip", "install", "-r", str(requirements_file)])
    sys.path.append(str(projects_dir / "src"))
    sys.path.append(str(projects_dir.parent))


def run_test_on_projects():
    is_successful = True
    dynapyt_dir = Path(__file__).parent.parent
    execution_invariance_test_dir = Path(__file__).parent
    test_folders_file = execution_invariance_test_dir / "test_folders.txt"
    with open(test_folders_file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            projects_dir = dynapyt_dir / line.strip()
            if not run_tests(projects_dir):
                is_successful = False
                break

    if is_successful:
        print("All tests passed for all projects")
    else:
        print("Some tests failed")
    return is_successful


if __name__ == "__main__":
    run_test_on_projects()