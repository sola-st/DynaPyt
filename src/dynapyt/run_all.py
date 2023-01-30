import argparse
import os
from pathlib import Path
import shutil
from subprocess import run
from os import walk
from os import path
import time
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument(
    "--directory", help="Directory of the project to analyze")
parser.add_argument(
    "--entry", help="Entry module of the execution")
parser.add_argument(
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--skip-instrumentation", help="Skip instrumentation", action='store_true')
parser.add_argument(
    "--time-limit", help="Time limit for instrumentation in minutes")
parser.add_argument(
    "--module", help="Adds external module paths")


def process_files(cmd_list, file_path):
    comp_proc = run(cmd_list)
    if comp_proc.returncode != 0:
        print('Error at', file_path)
        exit(0)

if __name__ == '__main__':
    args = parser.parse_args()
    start = args.directory
    analysis = args.analysis
    entry = args.entry
    module = args.module
    start_time = time.time()
    all_cmds = []
    
    if args.skip_instrumentation != True:
        for dir_path, dir_names, file_names in walk(start):
            if (args.time_limit is not None) and ((time.time() - start_time)/60 > int(args.time_limit)):
                break
            for name in file_names:
                if name.endswith('.py'):
                    file_path = path.join(dir_path, name)
                    cmd_list = ['python', '-m', 'dynapyt.instrument.instrument', '--files', file_path, '--analysis', analysis, '--module', module]
                    all_cmds.append((cmd_list, file_path))
        with Pool() as p:
            p.starmap(process_files, all_cmds)
    
    run(['python', '-m', 'dynapyt.run_analysis', '--entry', entry, '--analysis', analysis, '--module', module])
