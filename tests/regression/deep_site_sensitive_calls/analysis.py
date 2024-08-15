from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def pre_call(self, dyn_ast: str, iid: int, function, pos_args, kw_args) -> None:
        print(f"pre call of {function.__name__}")

    def binary_operation(self, dyn_ast, iid, op, left, right, result):
        print(f"binary operation {left} {op} {right} = {result}")

    def end_execution(self) -> None:
        print("end execution")
