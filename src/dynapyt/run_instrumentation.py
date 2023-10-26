from typing import List, Set
import argparse
from os import walk
from os import path
from pathlib import Path
import shutil
from subprocess import run
import time
from multiprocessing import Pool


def instrument_dir(
    directory: str,
    analysis: List[str],
    use_external_dir: bool = False,
    exclude: Set[str] = set(),
):
    start_time = time.time()
    start = directory
    all_cmds = []

    if use_external_dir:
        external_path = Path(start) / "dynapyt_analysis"
        # create new folder /dynapyt_analysis on same level as specified directory
        shutil.rmtree(external_path, ignore_errors=True)
        shutil.copytree(start, external_path)
        start = str(external_path)

    for dir_path, dir_names, file_names in walk(start):
        for name in dir_names:
            if path.join(dir_path, name) in exclude:
                dir_names.remove(name)
        for name in file_names:
            file_path = path.join(dir_path, name)
            if name.endswith(".py") and file_path not in exclude:
                cmd_list = [
                    "python",
                    "-m",
                    "dynapyt.instrument.instrument",
                    "--files",
                    file_path,
                    "--analysis",
                ] + analysis
                all_cmds.append((cmd_list, file_path))
    with Pool(maxtasksperchild=5) as p:
        p.starmap(process_files, all_cmds)
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
        required=True,
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
    use_external_dir = args.external_dir
    instrument_dir(start, analysis, use_external_dir)
