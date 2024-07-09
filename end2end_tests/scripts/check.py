import fire
import json
from pathlib import Path
from dynapyt.utils.runtimeUtils import match_output, match_coverage


def check(project_dir: str, output_dir: str, coverage_dir: str):
    with open(Path(output_dir) / "output.json", "r") as f:
        output = json.load(f)
    with open(Path(project_dir) / "expected_output.json", "r") as f:
        expected = json.load(f)["output"]
    if not match_output(output, expected):
        raise ValueError(
            f"Output does not match expected output: Expected:\n{expected}\nActual:\n{output}\n"
        )

    with open(Path(coverage_dir) / "coverage.json", "r") as f:
        coverage = json.load(f)
    with open(Path(project_dir) / "expected_coverage.json", "r") as f:
        expected = json.load(f)
    if not match_coverage(coverage, expected):
        raise ValueError(
            f"Coverage does not match expected coverage: Expected:\n{expected}\nActual:\n{coverage}\n"
        )


if __name__ == "__main__":
    fire.Fire(check)
