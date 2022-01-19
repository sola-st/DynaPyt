import libcst as cst

analysis = None

def set_analysis(new_analysis):
    global analysis
    analysis = new_analysis

def call_if_exists(f, *args):
    try:
        func = getattr(analysis, f)
        return func(*args)
    except AttributeError:
        return

def _dynapyt_parse_to_ast_(code):
    return cst.parse_module(code)

def _assign_(iid, right):
    result = call_if_exists('assignment', iid, '', None, right)
    return result if result != None else right

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
    result_new = call_if_exists('binary_op', iid, bin_op[opr], left, right, result)
    return result_new if result_new != None else result

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
    result_new = call_if_exists('unary_op', iid, un_op[opr], right, result)
    return result_new if result_new != None else result

def _comp_op_(iid, left, comparisons):
    comp_op = ['Equal', 'GreaterThan', 'GreaterThanEqual', 'In', 'Is', 'LessThan',
        'LessThanEqual', 'NotEqual', 'IsNot', 'NotIn']
    l = left
    result = True
    for op, r in comparisons:
        if op == 0:
            tmp = l == r
        elif op == 1:
            tmp = l > r
        elif op == 2:
            tmp = l >= r
        elif op == 3:
            tmp = l in r
        elif op == 4:
            tmp = l is r
        elif op == 5:
            tmp = l < r
        elif op == 6:
            tmp = l <= r
        elif op == 7:
            tmp = l != r
        elif op == 8:
            tmp = l is not r
        elif op == 9:
            tmp = l not in r
        result = result and tmp
    result_new = call_if_exists('comparison', iid, left, [(comp_op[i], j) for i, j in comparisons], result)
    return result_new if result_new != None else result

def _call_(iid, call):
    call_if_exists('pre_call', iid)
    result = call()
    call_if_exists('post_call', iid)
    return result

def _literal_(iid, val):
    res = call_if_exists('literal', iid, val)
    return res if res != None else val

def _delete_(iid, del_expr):
    del_expr()

def _raise_(iid, raise_arg):
    raise_arg()

def _catch_(exception):
    raise exception

def _read_var_(iid, name_arg, var_arg):
    value = var_arg()
    result = call_if_exists('read_var', iid, name_arg, value, False)
    return result if result != None else value

def _condition_(iid, val):
    result = call_if_exists('condition', iid, val)
    return result if result != None else val

def _func_entry_(iid):
    return

def _func_exit_(iid, return_val):
    return return_val

def _jump_(iid, is_break):
    return True

def _enter_ctrl_flow_(iid, condition):
    call_if_exists('enter_ctrl_flow', iid, condition)
    return condition

def _exit_ctrl_flow_(iid):
    call_if_exists('exit_ctrl_flow', iid)