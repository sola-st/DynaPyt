from os import walk
from os.path import realpath, dirname, sep


def pytest_generate_tests(metafunc):
    # find all subdirectories that contain a micro-test
    directories = []
    current_dir = dirname(realpath(__file__))
    test_ids = []
    for root, dirs, files in walk(current_dir):
        if all([f in files for f in ["program.py", "analysis.py", "expected.txt"]]):
            relative_path = root[len(current_dir)+len(sep):]
            directories.append([root, relative_path])
            test_ids.append(relative_path)

    # invoke the test in each directory
    metafunc.parametrize("directory_pair", directories, ids=test_ids)
