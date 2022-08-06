import argparse
from subprocess import run
from os import walk
from os import path
import time
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument(
    "--directory", help="Directory of the project to analyze")
parser.add_argument(
    "--analysis", help="Analysis class name")

def process_files(cmd_list, file_path):
    comp_proc = run(cmd_list)
    if comp_proc.returncode != 0:
        print('Error at', file_path)

if __name__ == '__main__':
    args = parser.parse_args()
    start = args.directory
    print(start)
    analysis = args.analysis
    start_time = time.time()
    all_cmds = []
    for dir_path, dir_names, file_names in walk(start):
        for name in file_names:
            if (name in ['setup.py', '__init__.py', '__version__.py']) or ('config' in name):
                continue
            if name.endswith('.py'):
                file_path = path.join(dir_path, name)
                cmd_list = ['python', '-m', 'dynapyt.instrument.instrument', '--files', file_path, '--analysis', analysis]
                all_cmds.append((cmd_list, file_path))
    with Pool(maxtasksperchild=5) as p:
        p.starmap(process_files, all_cmds)
    print('#################### Instrumentation took ' + str(time.time() - start_time))
