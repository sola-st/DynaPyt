from typing import List
import argparse
import importlib
from os.path import abspath
import sys
import signal


def run_analysis(entry: str, analyses: List[str], name: str = None):
    my_analyses = []
    try:
        for analysis in analyses:
            module = importlib.import_module(".".join(analysis.split(".")[:-1]))
            class_ = getattr(module, analysis.split(".")[-1])
            my_analyses.append(class_())
    except TypeError as e:
        print(f"--module was used but no value specified {e}")
    except ImportError as e:
        print(f"module could not be imported {e}")

    rt.set_analysis(my_analyses)

    def end_execution():
        try:
            for my_analysis in my_analyses:
                func = getattr(my_analysis, "end_execution")
                func()
        except AttributeError:
            pass

    # allow dynapyt to exit gracefully
    signal.signal(signal.SIGINT, end_execution)
    signal.signal(signal.SIGTERM, end_execution)

    if not name is None:
        for my_analysis in my_analyses:
            getattr(my_analysis, "add_metadata", lambda: None)({"name": name})

    try:
        for my_analysis in my_analyses:
            func = getattr(my_analysis, "begin_execution")
            func()
    except AttributeError:
        pass
    if entry.endswith(".py"):
        sys.argv = [entry]
        entry_full_path = abspath(entry)
        globals_dict = globals().copy()
        globals_dict["__file__"] = entry_full_path
        exec(open(entry_full_path).read(), globals_dict)
    else:
        importlib.import_module(entry, "*")
    end_execution()


parser = argparse.ArgumentParser()
parser.add_argument("--entry", help="Entry file for execution")
parser.add_argument("--analysis", help="Analysis class name(s)", nargs="+")
parser.add_argument("--name", help="Associates a given name with current run")

import dynapyt.runtime as rt

if __name__ == "__main__":
    args = parser.parse_args()
    name = args.name
    analyses = args.analysis
    run_analysis(args.entry, analyses, name)
