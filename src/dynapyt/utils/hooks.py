def snake(x):
    res = ''
    for i in range(len(x)-1):
        res += x[i]
        if ('a' <= x[i] <= 'z') and ('A' <= x[i+1] <= 'Z'):
            res += '_'
    res += x[-1]
    return '_' + res.lower() + '_'

def get_hooks_from_analysis(method_list):
    res = []
    if any(x in method_list for x in ['boolean_literal', 'literal']):
        res.append('boolean')
    if any(x in method_list for x in ['integer_literal', 'literal']):
        res.append('integer')
    if any(x in method_list for x in ['float_literal', 'literal']):
        res.append('float')
    if any(x in method_list for x in ['string_literal', 'literal']):
        res.append('string')
    if any(x in method_list for x in ['if_stmt', 'control_flow']):
        res.append('if')
    if any(x in method_list for x in ['for_stmt', 'control_flow']):
        res.append('for')
    if any(x in method_list for x in ['while_stmt', 'control_flow']):
        res.append('while')
    if any(x in method_list for x in ['break_stmt', 'control_flow']):
        res.append('break')
    if any(x in method_list for x in ['continue_stmt', 'control_flow']):
        res.append('continue')
    if any(x in method_list for x in ['mem_access', 'read']):
        res.append('read')
    if any(x in method_list for x in ['mem_access', 'write', 'assignment']):
        res.append('assignment')
    if any(x in method_list for x in ['mem_access', 'delete']):
        res.append('delete')
    if any(x in method_list for x in ['operation', 'binary_op']):
        res.append('binary_operation')
    if any(x in method_list for x in ['operation', 'unary_op']):
        res.append('unary_operation')
    if any(x in method_list for x in ['operation', 'comparison']):
        res.append('comparison')
    if any(x in method_list for x in ['pre_call', 'post_call']):
        res.append('call')
    if any(x in method_list for x in ['func_enter', 'func_exit']):
        res.append('function')
    if any(x in method_list for x in ['exception', 'raise_stmt']):
        res.append('raise')
    if any(x in method_list for x in ['attribute']):
        res.append('attribute')
    if any(x in method_list for x in ['subscript']):
        res.append('subscript')
    aug_assign_list = ['AddAssign', 'BitAndAssign', 'BitOrAssign', 'BitXorAssign', 'DivideAssign',
        'FloorDivideAssign', 'LeftShiftAssign', 'MatrixMultiplyAssign', 'ModuloAssign',
        'MultiplyAssign', 'PowerAssign', 'RightShiftAssign', 'SubtractAssign']
    if any(snake(x) in method_list for x in aug_assign_list):
        res.extend([x for x in aug_assign_list if snake(x) in method_list])
    bin_op_list = ['Add', 'BitAnd', 'BitOr', 'BitXor', 'Divide', 'FloorDivide',
        'LeftShift', 'MatrixMultiply', 'Modulo', 'Multiply', 'Power',
        'RightShift', 'Subtract', 'And', 'Or']
    if any(snake(x) in method_list for x in bin_op_list):
        res.extend([x for x in bin_op_list if snake(x) in method_list])
    un_op_list = ['BitInvert', 'Minus', 'Not', 'Plus']
    if any(snake(x) in method_list for x in un_op_list):
        res.extend([x for x in un_op_list if snake(x) in method_list])
    comp_op_list = ['Equal', 'GreaterThan', 'GreaterThanEqual', 'In', 'Is', 'LessThan',
        'LessThanEqual', 'NotEqual', 'IsNot', 'NotIn']
    if any(snake(x) in method_list for x in comp_op_list):
        res.extend([x for x in comp_op_list if snake(x) in method_list])
    # return res
    # return ['control_flow']
    return ['boolean', 'integer', 'float', 'string', 'imaginary', 'binary_operation', 'boolean_operation',
        'unary_operation', 'comparison', 'function', 'return', 'yield', 'call', 'exception', 'delete',
        'read', 'subscript', 'attribute', 'lambda', 'control_flow', 'assignment']