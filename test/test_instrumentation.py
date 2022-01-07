from os import walk, path
from dynapyt.instrument.instrument import instrument_code
from dynapyt.instrument.IIDs import IIDs
from shutil import move
import pytest

all_hooks = ['literal', 'unary_operation', 'binary_operation', 'control_flow', 'function', 'condition', 'read']

@pytest.fixture(autouse=True)
def reset():
    for (dirpath, dirnames, filenames) in walk(path.normpath(path.join(path.dirname(path.abspath(__file__)), '../sample_code'))):
        for f in filenames:
            if f.endswith('.py.orig'):
                move(path.join(dirpath, f), path.join(dirpath, f[:-5]))

def pytest_generate_tests(metafunc):
    test_f = []
    correct_f = []
    for (dirpath, dirnames, filenames) in walk(path.normpath(path.join(path.dirname(path.abspath(__file__)), '../sample_code'))):
        test_f.extend(path.join(dirpath, filename) for filename in filenames if filename.endswith('.py'))
        correct_f.extend(path.join(dirpath, filename+'.correct') for filename in filenames if filename.endswith('.py'))
    metafunc.parametrize("test_file,correct_file", list(zip(test_f, correct_f)), ids=[tf.split('/')[-1][:-3] for tf in test_f])

def test_instrumentation(test_file, correct_file):
    with open(test_file) as tf, open(correct_file) as cf:
        test_code = tf.read()
        correct_code = cf.read()
    instrumented_code = instrument_code(test_code, test_file, IIDs(None), all_hooks)
    if instrumented_code is None:
        instrumented_code = test_code
    l_ins_code = instrumented_code.split('\n')
    l_cor_code = correct_code.split('\n')
    for l1, l2 in zip(l_ins_code, l_cor_code):
        assert l1 == l2
    # assert instrumented_code == correct_code
