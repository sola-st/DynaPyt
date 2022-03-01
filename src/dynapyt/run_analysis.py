import argparse
import importlib
from subprocess import run
from os.path import abspath
import sys
from .instrument.IIDs import IIDs

parser = argparse.ArgumentParser()
parser.add_argument(
    "--entry", help="Entry file for execution")
parser.add_argument(
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--iids", help="IIDs json file")

import dynapyt.runtime as rt

if __name__ == '__main__':
    args = parser.parse_args()
    
    iids = IIDs(args.iids)
    module = importlib.import_module('dynapyt.analyses.' + args.analysis)
    class_ = getattr(module, args.analysis)
    try:
        my_analysis = class_(iids)
    except:
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