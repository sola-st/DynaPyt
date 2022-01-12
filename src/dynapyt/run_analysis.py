import argparse
import importlib

parser = argparse.ArgumentParser()
parser.add_argument(
    "--entry", help="Entry file for execution")
parser.add_argument(
    "--analysis", help="Analysis class name")

import dynapyt.runtime

if __name__ == '__main__':
    args = parser.parse_args()
    
    module = importlib.import_module('dynapyt.analyses.' + args.analysis)
    class_ = getattr(module, args.analysis)
    my_analysis = class_()
    dynapyt.runtime.set_analysis(my_analysis)
    importlib.import_module(args.entry, '*')