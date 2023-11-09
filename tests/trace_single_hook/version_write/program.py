import os

with open(os.sep.join(__file__.split(os.sep)[:-1]) + f"{os.sep}__init__.py", "r") as f:
    exec(f.read())
