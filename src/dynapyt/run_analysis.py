from shutil import rmtree
from typing import List
import argparse
import importlib
import os
from os.path import abspath
from tempfile import gettempdir
import sys
import uuid
import json
from pathlib import Path
from .utils.runtimeUtils import gather_coverage, gather_output
from .runtime import RuntimeEngine


def run_analysis(
    entry: str,
    analyses: List[str],
    name: str = None,
    output_dir: str = None,
    coverage: bool = False,
    coverage_dir: str = None,
    script: str = None,
) -> str:
    """
    The main function to run the analysis on instrumented code.
    This function also merges the output and coverage files from different analyses and/or processes.

    Parameters:
    ----------
    entry: str
        The entry file or module for execution
    analyses: List[str]
        The list of analysis classes (full access path)
    name: str
        Optional name to associate with the run
    output_dir: str
        Optional output directory
    coverage: bool
        Enable analysis coverage (False by default)
    coverage_dir: str
        Optional coverage directory
    script: str
        Optional script to execute. Note that if script is provided, entry will be ignored.

    Returns:
    -------
    str
        The session id for the current run
    """
    os.environ["DYNAPYT_SESSION_ID"] = session_id = str(uuid.uuid4())
    if coverage:
        if coverage_dir is None:
            coverage_dir = gettempdir()
        coverage_path = Path(coverage_dir) / f"dynapyt_coverage-{session_id}"
        os.environ["DYNAPYT_COVERAGE"] = str(coverage_path)
    elif "DYNAPYT_COVERAGE" in os.environ:
        del os.environ["DYNAPYT_COVERAGE"]

    analyses_file = Path(gettempdir()) / f"dynapyt_analyses-{session_id}.txt"
    if analyses_file.exists():
        analyses_file.unlink()
    if output_dir is None:
        output_dir = Path(gettempdir()) / f"dynapyt_output-{session_id}"
    else:
        output_dir = Path(output_dir) / f"dynapyt_output-{session_id}"
    if not output_dir.exists():
        output_dir.mkdir()
    else:
        rmtree(output_dir)
        output_dir.mkdir()
    analyses = [f"{a};output_dir={str(output_dir)}" for a in analyses]
    with open(str(analyses_file), "w") as f:
        f.write("\n".join(analyses))

    if script is None and not entry.endswith(".py"):
        if importlib.util.find_spec(entry) is None:
            raise ValueError(f"Could not find entry {entry}")
        importlib.import_module(entry)
    else:
        sys.argv = [entry]
        entry_full_path = abspath(entry)
        globals_dict = globals().copy()
        sys.path.insert(0, str(Path(entry_full_path).parent))
        globals_dict["__file__"] = entry_full_path
        if script is not None:
            exec(script, globals_dict)
        elif entry.endswith(".py"):
            exec(open(entry_full_path).read(), globals_dict)
    if RuntimeEngine._rt_engine is not None:
        RuntimeEngine().__del__()

    # read all files in output directory and merge them
    # gather_output(output_dir)

    # read all files in coverage directory and merge them
    # if coverage:
    #     gather_coverage(coverage_path)

    return session_id


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
    run_analysis(entry=args.entry, analyses=analyses, name=name, coverage=args.coverage)
