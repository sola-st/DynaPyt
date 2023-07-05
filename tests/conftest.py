from os import walk
from os.path import realpath, dirname, sep


def pytest_addoption(parser):
    parser.addoption(
        "--only",
        action="store",
        default=None,
        help="Run only the test in the specified directory",
    )


def pytest_generate_tests(metafunc):
    # find all subdirectories that contain a micro-test
    directories = []
    selection = metafunc.config.getoption("only", default=None, skip=False)
    if selection is not None:
        start_dir = realpath(selection)
    current_dir = dirname(realpath(__file__))
    if selection is None:
        start_dir = current_dir
    test_ids = []
    for root, dirs, files in walk(start_dir):
        if all([f in files for f in ["program.py", "analysis.py", "expected.txt"]]):
            relative_path = root[len(current_dir) + len(sep) :]
            directories.append([root, relative_path])
            test_ids.append(relative_path)

    # invoke the test in each directory
    metafunc.parametrize("directory_pair", directories, ids=test_ids)
