from typing import Iterable
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class SlowStringConcatAnalysis(BaseAnalysis):
    def __init__(self):
        super().__init__()
        self.in_loop = []
        self.concat_count = []
        self.threshold = 5

    def enter_for(self, dyn_ast: str, iid: int, next_value, iterable: Iterable):
        if (
            self.in_loop
            and self.in_loop[-1][0] == dyn_ast
            and self.in_loop[-1][1] == iid
        ):
            pass
        else:
            self.in_loop.append((dyn_ast, iid))
            self.concat_count.append(0)

    def exit_for(self, dyn_ast: str, iid: int):
        curr = self.in_loop.pop()
        assert curr[0] == dyn_ast
        assert curr[1] == iid
        self.concat_count.pop()

    def add_assign(self, dyn_ast: str, iid: int, lhs, rhs):
        if self.in_loop:
            if isinstance(rhs, str):
                self.concat_count[-1] += 1
            if self.concat_count[-1] >= self.threshold:
                print(f"Possible slow string concatenation in {dyn_ast} at {iid}")
