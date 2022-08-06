import argparse
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
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--module", help="Adds external module paths")

def process_files(cmd_list, file_path):
    comp_proc = run(cmd_list)
    if comp_proc.returncode != 0:
        print('Error at', file_path)

if __name__ == '__main__':
    args = parser.parse_args()
    start = args.directory
    analysis = args.analysis
    module = args.module
    start_time = time.time()
    all_cmds = []

    # move up one directory
    # remove last slash in case a path like /some/path
    # is specified
    if start[-1] == '/':
        start = start[:-1]
    working_dir = start.rsplit('/',1)[0]
    working_dir += '/dynapyt_analysis'
    shutil.rmtree(working_dir, ignore_errors=True)
    shutil.copytree(start, working_dir)
    for dir_path, dir_names, file_names in walk(working_dir):
        for name in file_names:
            if name.endswith('.py'):
                file_path = path.join(dir_path, name)
                cmd_list = ['python', '-m', 'dynapyt.instrument.instrument', '--files', file_path, '--analysis', analysis]
                if module is not None:
                    cmd_list.extend(['--module', module])
                all_cmds.append((cmd_list, file_path))
    with Pool(maxtasksperchild=5) as p:
        p.starmap(process_files, all_cmds)
    print('--------> ' + str(time.time() - start_time))
