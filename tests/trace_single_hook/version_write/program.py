import os

with open("/".join(__file__.split("/")[:-1]) + "/__init__.py", "r") as f:
    exec(f.read())
