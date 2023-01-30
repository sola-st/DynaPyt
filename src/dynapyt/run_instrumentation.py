import argparse
from os import walk
from os import path
from pathlib import Path
import shutil
from subprocess import run
import time
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument(
    "--directory", help="Directory of the project to analyze")
parser.add_argument(
    "--analysis", help="Analysis class name")
parser.add_argument(
    "--module", help="Adds external module paths")
parser.add_argument(
    "--external_dir", help="Place instrumented files in another directory",
    dest='external_dir', action='store_true'
)

def process_files(cmd_list, file_path):
    comp_proc = run(cmd_list)
    if comp_proc.returncode != 0:
        print('Error at', file_path)

if __name__ == '__main__':
    args = parser.parse_args()
    start = args.directory
    analysis = args.analysis
    module = args.module
    use_external_dir = args.external_dir
    start_time = time.time()
    all_cmds = []

    if use_external_dir:
        external_path = Path(start) / "dynapyt_analysis"
        # create new folder /dynapyt_analysis on same level as specified directory
        shutil.rmtree(external_path, ignore_errors=True)
        shutil.copytree(start, external_path)
        start = str(external_path)
    
    for dir_path, dir_names, file_names in walk(start):
        for name in file_names:
            if name.endswith('.py'):
                file_path = path.join(dir_path, name)
                cmd_list = ['python', '-m', 'dynapyt.instrument.instrument', '--files', file_path, '--analysis', analysis]
                if module is not None:
                    cmd_list.extend(['--module', module])
                all_cmds.append((cmd_list, file_path))
    with Pool(maxtasksperchild=5) as p:
        p.starmap(process_files, all_cmds)
    print('#################### Instrumentation took ' + str(time.time() - start_time))
