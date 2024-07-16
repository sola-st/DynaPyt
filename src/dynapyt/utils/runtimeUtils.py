import importlib
import json
from pathlib import Path
from typing import List, Any
from ..analyses.BaseAnalysis import BaseAnalysis


def load_analyses(analyses: List[Any]) -> List[BaseAnalysis]:
    res_analyses = []
    for ana in analyses:
        if isinstance(ana, str) and "." in ana:
            conf = None
            if ";" in ana:
                parts = ana.split(";")
                ana = parts[0]
                conf = {p.split("=")[0]: p.split("=")[1] for p in parts[1:]}
            module_parts = ana.split(".")
            module = importlib.import_module(".".join(module_parts[:-1]))
            class_ = getattr(module, module_parts[-1])
            if conf is not None:
                res_analyses.append(class_(**conf))
            else:
                res_analyses.append(class_())
        elif isinstance(ana, BaseAnalysis):
            res_analyses.append(ana)
        else:
            continue
    return res_analyses


def merge_coverage(base_coverage: dict, new_coverage: dict) -> dict:
    for cov_file, coverage in new_coverage.items():
        if cov_file not in base_coverage:
            base_coverage[cov_file] = {}
        for line, analysis_cov in coverage.items():
            if line not in base_coverage[cov_file]:
                base_coverage[cov_file][line] = {}
            for analysis, count in analysis_cov.items():
                if analysis not in base_coverage[cov_file][line]:
                    base_coverage[cov_file][line][analysis] = 0
                base_coverage[cov_file][line][analysis] += count
    return base_coverage


def gather_coverage(coverage_path: Path) -> None:
    analysis_coverage = {}
    for cov_file in coverage_path.glob("coverage-*.json"):
        with open(coverage_path / cov_file, "r") as f:
            new_coverage = json.load(f)
            analysis_coverage = merge_coverage(analysis_coverage, new_coverage)
        (coverage_path / cov_file).unlink()
    with open(coverage_path / "coverage.json", "w") as f:
        json.dump(analysis_coverage, f)


def gather_output(output_dir: Path) -> None:
    analysis_output = []
    for output_file in output_dir.glob("output-*.json"):
        with open(output_dir / output_file, "r") as f:
            new_output = json.load(f)
            analysis_output.append(new_output)
        (output_dir / output_file).unlink()
    with open(output_dir / "output.json", "w") as f:
        json.dump(analysis_output, f, indent=2)


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


def match_coverage(actual: dict, expected: dict) -> bool:
    return expected == {
        k.replace("\\", "/").replace("//", "/").split("/projects/")[-1]: v
        for k, v in actual.items()
    }
