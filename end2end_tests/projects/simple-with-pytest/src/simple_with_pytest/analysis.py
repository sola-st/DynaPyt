# DYNAPYT: DO NOT INSTRUMENT

import json
from uuid import uuid4
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class Analysis(BaseAnalysis):
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir
        self.output = []

    def begin_execution(self):
        self.output.append("begin execution")

    def end_execution(self):
        self.output.append("end execution")
        with open(f"{self.output_dir}/output-{str(uuid4())}.json", "w") as f:
            json.dump(self.output, f, indent=2)

    def binary_operation(self, dyn_ast, iid, op, left, right, result):
        self.output.append(f"{left} {op} {right} = {result}")
