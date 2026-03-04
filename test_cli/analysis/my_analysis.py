from dynapyt.analyses.BaseAnalysis import BaseAnalysis
from pathlib import Path

class MyAnalysis(BaseAnalysis):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_call(self, dyn_ast, iid, call, pos_args, kw_args):
        print(f"Call at {iid} in {dyn_ast}")
        with open(Path(self.output_dir) / "output.txt", "a") as f:
            f.write(f"Call at {iid} in {dyn_ast}\n")
        
