import os
import pathlib

root = '/home/eghbalaz/Documents/PhD/Projects/pandas_dynapyt/pandas/tests'
for path, subdirs, files in os.walk(root):
    for name in files:
        if name.endswith('.py'):
            print(pathlib.PurePath(path, name))