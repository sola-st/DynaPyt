import argparse
import importlib
from os.path import abspath
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "--entry", help="Entry file for execution")
parser.add_argument(
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--module", help="Adds external module paths")

import dynapyt.runtime as rt

if __name__ == '__main__':
    args = parser.parse_args()
    additional_module = args.module
    analysis = args.analysis
    modulePath = 'dynapyt.analyses'
    if additional_module is not None:
        modulePath = additional_module
    try:
        module = importlib.import_module(modulePath + '.' + analysis)
    except TypeError as e:
        print(f'--module was used but no value specified {e}')
    except ImportError as e:
        print(f'module could not be imported {e}')

    class_ = getattr(module, args.analysis)
    my_analysis = class_()
    rt.set_analysis(my_analysis)
    try:
        func = getattr(my_analysis, 'begin_execution')
        func()
    except AttributeError:
        pass
    if args.entry.endswith('.py'):
        sys.argv = [args.entry]
        exec(open(abspath(args.entry)).read())
    else:
        importlib.import_module(args.entry, '*')
    try:
        func = getattr(my_analysis, 'end_execution')
        func()
    except AttributeError:
        pass