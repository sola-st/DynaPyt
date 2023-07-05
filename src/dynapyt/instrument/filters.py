from typing import Dict, List
import functools

SEPERATOR = "<dySep>"
START = "DynaPyt internal:"
END = ":DynaPyt internal"


def only(patterns=[]):
    def decorator_only(func):
        if len(patterns) > 0:
            if func.__doc__ is None:
                func.__doc__ = ""
            func.__doc__ += f"{START} only -> {SEPERATOR.join(patterns)} {END}"

        @functools.wraps(func)
        def only_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return only_wrapper

    return decorator_only


def ignore(patterns=[]):
    def decorator_ignore(func):
        if len(patterns) > 0:
            if func.__doc__ is None:
                func.__doc__ = ""
            func.__doc__ += f"{START} ignore -> {SEPERATOR.join(patterns)} {END}"

        @functools.wraps(func)
        def ignore_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return ignore_wrapper

    return decorator_ignore


def get_details(func) -> Dict[str, List[str]]:
    if func.__doc__ is None:
        return {}
    start = func.__doc__.find(START)
    if start == -1:
        return {}
    end = func.__doc__.find(END)
    if end == -1:
        return {}
    specs = func.__doc__[start + len(START) : end]
    details = {}
    if specs.strip().startswith("only ->"):
        details["only"] = specs.strip().split(" -> ")[1].split(SEPERATOR)
    elif specs.strip().startswith("ignore ->"):
        details["ignore"] = specs.strip().split(" -> ")[1].split(SEPERATOR)
    return details
