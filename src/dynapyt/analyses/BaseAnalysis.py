import logging
import libcst as cst

class BaseAnalysis:

    def __init__(self) -> None:
        self.asts = {}
        self.danger_of_recursion = False
        logging.basicConfig(filename='output.log', format='%(message)s', encoding='utf-8', level=logging.INFO)
    
    def __log(self, *args):
        res = ''
        for arg in args:
            if self.danger_of_recursion:
                res += ' ' + str(hex(id(arg)))
            else:
                res += ' ' + str(arg)
        logging.info(res[:80])
    
    def __get_ast(self, filepath: str) -> cst.CSTNodeT:
        if filepath not in self.asts:
            src = ''
            with open(filepath, 'r') as file:
                src = file.read()
            self.asts[filepath] = cst.parse_module(src)

        return self.asts[filepath]