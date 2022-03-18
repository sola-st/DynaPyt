# https://docs.quantifiedcode.com/python-anti-patterns/performance/using_key_in_list_to_check_if_key_is_contained_in_a_list.html
from .BaseAnalysis import BaseAnalysis

class KeyInListAnalysis(BaseAnalysis):
    def __init__(self):
        self.threshold = 100

    def _in(self, dyn_ast, iid, left, right, result):
        if isinstance(right, list) and len(right) > self.threshold:
            print('Dynapyt warning: checking key in list is less efficient than checking key in set')
    
    def not_in(self, dyn_ast, iid, left, right, result):
        if isinstance(right, list) and len(right) > self.threshold:
            print('Dynapyt warning: checking key in list is less efficient than checking key in set')
