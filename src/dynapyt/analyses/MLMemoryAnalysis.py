# Inspired by https://pytorch.org/docs/stable/notes/faq.html#my-model-reports-cuda-runtime-error-2-out-of-memory
from collections import defaultdict
from .BaseAnalysis import BaseAnalysis

class MLMemoryAnalysis(BaseAnalysis):
    def __init__(self) -> None:
        super().__init__()
        self.in_ctrl_flow = []
        self.threshold = 3
        self.memory_leak = defaultdict(lambda: 0)
        self.last_opr = None
    
    def enter_control_flow(self, dyn_ast, iid, condition):
        self.last_opr = None
        if (len(self.in_ctrl_flow) > 0) and (self.in_ctrl_flow[-1] != iid):
            self.in_ctrl_flow.append(iid)
    
    def exit_control_flow(self, dyn_ast, iid):
        self.last_opr = None
        self.in_ctrl_flow.pop()
    
    def binary_operation(self, dyn_ast, iid, opr, left, right, res):
        if (len(self.in_ctrl_flow) > 0) and right.requires_grad:
            self.last_opr = iid
        else:
            self.last_opr = None
    
    def write(self, dyn_ast, iid, left, right):
        if (len(self.in_ctrl_flow) > 0) and right.requires_grad and (self.last_opr is not None):
            cur = (iid, self.in_ctrl_flow[-1])
            self.memory_leak[cur] += 1
            if self.memory_leak[cur] > 3:
                print('Memory issue detected')
                exit(1)
        self.last_opr = None