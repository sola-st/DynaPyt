import linecache
import sys
import pytest

bad_tests = set()
results = []
print(' '.join(sys.argv))
test_dir = sys.argv[-1]

def find_testfile(frame, package_test_dir):
    while frame is not None:
        if package_test_dir in frame.f_code.co_filename:
            ln = frame.f_lineno
            current_line = linecache.getline(frame.f_code.co_filename, ln)
            current_indent = len(current_line) - len(current_line.lstrip())
            while ln > 0:
                ln -= 1
                this_line = linecache.getline(frame.f_code.co_filename, ln)
                if len(this_line) - len(this_line.lstrip()) < current_indent and this_line.lstrip().startswith('def '):
                    bad_tests.add((frame.f_code.co_filename + '::' + linecache.getline(frame.f_code.co_filename, ln).strip()[4:].split('(')[0]).split('/')[-1])
                    break
        frame = frame.f_back

def uses_stack(frame, event, arg=None):
    code = frame.f_code
    access_path_names = code.co_names
    file_name = code.co_filename
    
    if '.'.join(access_path_names) in ['sys._getframe', 'sys.exc_info', 'inspect.stack']:
        find_testfile(frame, test_dir)
    elif file_name.endswith('inspect.py') and any(map(lambda x: x in linecache.getline(file_name, frame.f_lineno), ['trace', 'stack', 'currentframe', 'getinnerframes', 'getouterframes', 'getlineno', 'getframeinfo'])):
        find_testfile(frame, test_dir)
    return uses_stack

sys.settrace(uses_stack)

pytest.main(sys.argv[1:])

print('\n'.join(bad_tests))
with open('filtered.txt', 'w') as f:
    f.write('\n'.join(bad_tests))