import json
import builtins
import keyword
import importlib.resources

def snake(x):
    res = ''
    for i in range(len(x)-1):
        res += x[i]
        if ('a' <= x[i] <= 'z') and ('A' <= x[i+1] <= 'Z'):
            res += '_'
    res += x[-1]
    return res.lower()

def get_name(s):
    if (s in dir(builtins)) or (keyword.iskeyword(s)):
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
            if len(v.items()) > 0:
                res.extend(all_leaves(v))
            else:
                res.append(k)
        else:
            res.extend(get_used_leaves(v, method_list))
    return res

def get_hooks_from_analysis(method_list):
    with importlib.resources.open_text('dynapyt.utils', 'hierarchy.json') as f:
        hierarchy = json.load(f)
    return set(get_used_leaves(hierarchy, method_list))