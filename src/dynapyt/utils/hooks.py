from typing import Dict, List

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
import json
import builtins
import keyword
import importlib

from ..instrument.filters import START, END, SEPERATOR, get_details
from .load_analysis import load_analyses


def snake(x):
    res = ""
    for i in range(len(x) - 1):
        res += x[i]
        if ("a" <= x[i] <= "z") and ("A" <= x[i + 1] <= "Z"):
            res += "_"
    res += x[-1]
    return res.lower()


def get_name(s):
    if (s in dir(builtins)) or (keyword.iskeyword(s)):
        return "_" + s
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


def get_used_leaves(
    root, methods: Dict[str, Dict[str, List[str]]]
) -> Dict[str, Dict[str, List[str]]]:
    if len(root.items()) == 0:
        return {}
    res = {}
    for hook, children in root.items():
        if hook in methods:
            if len(children.items()) > 0:
                for leaf in all_leaves(children):
                    res.update({leaf: methods[hook]})
            else:
                res.update({hook: methods[hook]})
        else:
            res.update(get_used_leaves(children, methods))
    return res


def get_hooks_from_analysis(classes: List[str]) -> Dict[str, Dict[str, List[str]]]:
    try:
        methods = {}
        analyses = load_analyses(classes)
        for instance in analyses:
            methods.update(
                {
                    func: get_details(getattr(instance, func))
                    for func in dir(instance)
                    if callable(getattr(instance, func))
                    and not func.startswith("__")
                    and (
                        (func not in methods)
                        or (methods[func] == get_details(getattr(instance, func)))
                    )
                }
            )
    except TypeError as e:
        raise e
    except ImportError as e:
        raise e
    with pkg_resources.open_text("dynapyt.utils", "hierarchy.json") as f:
        hierarchy = json.load(f)
    return get_used_leaves(hierarchy, methods)
