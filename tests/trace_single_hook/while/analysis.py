from dynapyt.analyses.BaseAnalysis import BaseAnalysis

# dynapyt analysis class to track while
class TestAnalysis(BaseAnalysis):
    def begin_execution(self) -> None:
        print("begin execution")

    def enter_control_flow(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        print(f"enter control flow event with condition {cond_value}")
        # def iid_to_location(self, dyn_ast, iid) -> Location
        # namedtuple('Location', ["file", "start_line", "start_column", "end_line", "end_column"])
        print(f'at file {self.iid_to_location(dyn_ast, iid).file} line {self.iid_to_location(dyn_ast, iid).start_line}')

    def enter_while(self, dyn_ast: str, iid: int, cond_value: bool) -> Optional[bool]:
        print(f"while condition evaluates to {cond_value}")
        # print(f"at file {self.iid_to_location(dyn_ast, iid).filepath} line {self.iid_to_location(dyn_ast, iid).lineno}")
        # print(f"at file {self.iid_to_location[iid].file}, line {self.iid_to_location[iid].start_line}")
    
    def exit_while(self, dyn_ast: str, iid: int):
        print(f"done with while statement")

    def exit_control_flow(self, dyn_ast: str, iid: int) -> None:
        print(f"done with control flow statement")

    def end_execution(self) -> None:
        print("end execution")

# Analysis class to track while
class Analysis:
    def __init__(self):
        self.count = 0

    def trace(self, frame, event, arg):
        if event == "line":
            if frame.f_code.co_name == "test":
                self.count += 1
        return self.trace
