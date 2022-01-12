import libcst as cst

analysis = None

def set_analysis(new_analysis):
    global analysis
    analysis = new_analysis

def _dynapyt_parse_to_ast_(code):
    return cst.parse_module(code)

def _assign_(iid, right):
    result = analysis.assignment(iid, right)
    return result

def _binary_op_(iid, left, opr, right):
    bin_op = ['Add', 'BitAnd', 'BitOr', 'BitXor', 'Divide', 'FloorDivide',
        'LeftShift', 'MatrixMultiply', 'Modulo', 'Multiply', 'Power',
        'RightShift', 'Subtract', 'And', 'Or']
    if opr == 0:
        result = left + right
    elif opr == 1:
        result = left & right
    elif opr == 2:
        result = left | right
    elif opr == 3:
        result = left ^ right
    elif opr == 4:
        result = left / right
    elif opr == 5:
        result = left // right
    elif opr == 6:
        result = left << right
    elif opr == 7:
        result = left @ right
    elif opr == 8:
        result = left % right
    elif opr == 9:
        result = left * right
    elif opr == 10:
        result = left ** right
    elif opr == 11:
        result = left >> right
    elif opr == 12:
        result = left - right
    elif opr == 13:
        result = left and right
    elif opr == 14:
        result = left or right
    result = analysis.binary_op(iid, bin_op[opr], left, right, result)
    return result

def _unary_op_(iid, opr, right):
    un_op = ['BitInvert', 'Minus', 'Not', 'Plus']
    if opr == 0:
        result = ~ right
    elif opr == 1:
        result = - right
    elif opr == 2:
        result = not right
    elif opr == 3:
        result = + right
    result = analysis.unary_op(iid, un_op[opr], right, result)
    return result

def _call_(iid, call):
    return call()

def _literal_(iid, val):
    res = analysis.literal(iid, val)
    return res

def _delete_(iid, del_expr):
    del_expr()

def _raise_(iid, raise_arg):
    raise_arg()

def _catch_(exception):
    raise exception

def _read_var_(iid, var_arg):
    return var_arg()

def _condition_(iid, val):
    return val

def _func_entry_(iid):
    return

def _func_exit_(iid, return_val):
    return return_val

def _jump_(iid, is_break):
    return True