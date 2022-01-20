def get_hooks_from_analysis(method_list):
    res = []
    if any(x in method_list for x in ['number', 'string', 'boolean', 'literal']):
        res.append('literal')
    if any(x in method_list for x in ['if', 'for', 'while', 'break', 'continue']):
        res.append('control_flow')
    if any(x in method_list for x in ['mem_access', 'read_var', 'read_attr']):
        res.append('read')
    if any(x in method_list for x in ['mem_access', 'write_var', 'write_attr', 'assignment']):
        res.append('assignment')
    if any(x in method_list for x in ['mem_access', 'del_var', 'del_attr']):
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
    return res