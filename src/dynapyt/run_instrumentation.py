from typing import List, Set
import argparse
from os import walk
from os import path
from pathlib import Path
import shutil
from subprocess import run
import time
from multiprocessing import Pool
from dynapyt.utils.hooks import get_hooks_from_analysis
from dynapyt.instrument.instrument import instrument_files


def instrument_dir(
    directory: str,
    analysis: List[str],
    use_external_dir: bool = False,
    exclude: Set[str] = set(),
):
    start_time = time.time()
    start = directory
    all_cmds = []

    if isinstance(analysis, str) and Path(analysis).exists():
        with open(analysis, "r") as f:
            analysis = [ana.strip() for ana in f.read().split("\n")]

    if use_external_dir:
        external_path = Path(start) / "dynapyt_analysis"
        # create new folder /dynapyt_analysis on same level as specified directory
        shutil.rmtree(external_path, ignore_errors=True)
        shutil.copytree(start, external_path)
        start = str(external_path)

    files = [str(f.resolve()) for f in Path(start).rglob("*.py") if f not in exclude]
    instrument_files(files, analysis)
    print("#################### Instrumentation took " + str(time.time() - start_time))


def process_files(cmd_list, file_path):
    comp_proc = run(cmd_list)
    if comp_proc.returncode != 0:
        print("Error at", file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory", help="Directory of the project to analyze", required=True
    )
    parser.add_argument(
        "--analysis",
        help="Analysis class(es) (full dotted path)",
        nargs="+",
    )
    parser.add_argument(
        "--analysisFile",
        help="Analysis file with list of analysis classes",
    )
    parser.add_argument(
        "--external_dir",
        help="Place instrumented files in another directory",
        dest="external_dir",
        action="store_true",
    )
    args = parser.parse_args()
    start = args.directory
    analysis = args.analysis
    if args.analysisFile:
        analysis = args.analysisFile
    use_external_dir = args.external_dir
    instrument_dir(start, analysis, use_external_dir)
