from typing import List
import argparse
import importlib
from os.path import abspath
from tempfile import gettempdir
import sys
from pathlib import Path
from . import runtime as _rt


def run_analysis(
    entry: str,
    analyses: List[str],
    name: str = None,
    coverage: bool = False,
    coverage_dir: str = None,
):
    global _rt
    _rt = importlib.reload(_rt)

    if coverage:
        if coverage_dir is None:
            coverage_path = Path(gettempdir()) / "dynapyt_coverage"
            coverage_path.mkdir(exist_ok=True)
        else:
            coverage_path = Path(coverage)
            coverage_path.mkdir(exist_ok=True)
        _rt.set_coverage(coverage_path)
    else:
        _rt.set_coverage(None)

    analyses_file = Path(gettempdir()) / "dynapyt_analyses.txt"
    if analyses_file.exists():
        analyses_file.unlink()
    with open(str(analyses_file), "w") as f:
        f.write("\n".join(analyses))

    _rt.set_analysis(analyses)

    for analysis in _rt.analyses:
        func = getattr(analysis, "begin_execution", None)
        if func is not None:
            func()
    if entry.endswith(".py"):
        sys.argv = [entry]
        entry_full_path = abspath(entry)
        globals_dict = globals().copy()
        sys.path.insert(0, str(Path(entry_full_path).parent))
        globals_dict["__file__"] = entry_full_path
        exec(open(entry_full_path).read(), globals_dict)
    else:
        if importlib.util.find_spec(entry) is None:
            raise ValueError(f"Could not find entry {entry}")
        importlib.import_module(entry)
    _rt.end_execution()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", help="Entry file for execution", required=True)
    parser.add_argument(
        "--analysis", help="Analysis class name(s)", nargs="+", required=True
    )
    parser.add_argument("--name", help="Associates a given name with current run")
    parser.add_argument("--coverage", help="Enables coverage", action="store_true")
    args = parser.parse_args()
    name = args.name
    analyses = args.analysis
    run_analysis(args.entry, analyses, name, args.coverage)
