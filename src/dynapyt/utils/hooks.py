import json
import builtins

def snake(x):
    res = ''
    for i in range(len(x)-1):
        res += x[i]
        if ('a' <= x[i] <= 'z') and ('A' <= x[i+1] <= 'Z'):
            res += '_'
    res += x[-1]
    return '_' + res.lower() + '_'

def get_name(s):
    if s in dir(builtins):
        return '_' + s
    return s

def all_leaves(root):
    res = []
    l = [(k, v) for k, v in root.items()]
    while len(l) > 0:
        curr = l.pop()
        if len(curr[1].items()) == 0:
            res.append(curr[0])
        else:
            for k, v in curr[1].items():
                l.append((k, v))
    return res

def get_used_leaves(root, method_list):
    if len(root.items()) == 0:
        return []
    res = []
    for k, v in root.items():
        if get_name(k) in method_list:
            res.extend(all_leaves(v))
        else:
            res.extend(get_used_leaves(v, method_list))
    return res

def get_hooks_from_analysis(method_list):
    with open('hierarchy.json') as f:
        hierarchy = json.load(f)
    return get_used_leaves(hierarchy, method_list)
    # return ['boolean', 'integer', 'float', 'string', 'imaginary', 'binary_operation', 'boolean_operation',
    #     'unary_operation', 'comparison', 'function', 'return', 'yield', 'call', 'exception', 'delete',
    #     'read', 'subscript', 'attribute', 'lambda', 'control_flow', 'assignment', 'assert', 'dict', 'list', 'tuple']