"""
This module is DynaPyt's runtime engine.
It is not supposed to be used directly, but rather to be used by the instrumented code.
"""

from contextlib import contextmanager
from typing import List, Tuple, Any
from pathlib import Path
from sys import exc_info
import uuid
import atexit
import signal
import json
import sys
import os
from importlib import reload
from tempfile import gettempdir
import libcst as cst
from .utils.hooks import snake, get_name
from .instrument.IIDs import IIDs
from .instrument.filters import START, END, SEPERATOR
from .utils.runtimeUtils import load_analyses

analyses = None
covered = None
coverage_path = None
current_file = None
end_execution_called = False
engine_id = str(uuid.uuid4())
session_id = os.environ.get("DYNAPYT_SESSION_ID", None)
analyses_file = Path(gettempdir()) / f"dynapyt_analyses-{session_id}.txt"


def end_execution():
    global covered, coverage_path, end_execution_called
    if end_execution_called:
        return
    end_execution_called = True
    call_if_exists("end_execution")
    if covered is not None:
        with open(str(coverage_path), "w") as f:
            json.dump(covered, f)


def set_analysis():
    global analyses, analyses_file, end_execution_called
    if end_execution_called:
        reload(sys.modules[__name__])
        return
    analyses = []
    signal.signal(signal.SIGINT, end_execution)
    signal.signal(signal.SIGTERM, end_execution)
    atexit.register(end_execution)
    if analyses_file.exists():
        with open(str(analyses_file), "r") as af:
            new_analyses = af.read().split("\n")
    else:
        raise Exception(f"Analyses file not found: {str(analyses_file)}")
    analyses = load_analyses(new_analyses)
    for analysis in analyses:
        if hasattr(analysis, "begin_execution"):
            analysis.begin_execution()


set_analysis()


def set_coverage(coverage_dir: str):
    global covered, coverage_path, session_id
    print(f"Setting coverage for {coverage_dir}", file=sys.stderr)
    if coverage_dir is not None:
        coverage_dir = Path(coverage_dir)
        covered = {}
        session_id = str(coverage_dir).split("-")[-1]
        coverage_dir.mkdir(exist_ok=True)
        coverage_path = coverage_dir / f"coverage-{engine_id}.json"
        if coverage_path.exists():
            coverage_path.unlink()


set_coverage(os.environ.get("DYNAPYT_COVERAGE", None))


def filtered(func, f, args):
    docs = func.__doc__
    if docs is None or START not in docs:
        return False
    if len(args) >= 2:
        sub_args = args[2:]
    else:
        return False
    while START in docs:
        start = docs.find(START)
        end = docs.find(END)
        fltr = docs[start + len(START) : end].strip()
        patterns = fltr.split(" -> ")[1].split(SEPERATOR)
        if fltr.startswith("only ->") and any(
            [getattr(arg, "__name__", None) in patterns for arg in sub_args]
        ):
            return False
        elif fltr.startswith("ignore ->") and any(
            [getattr(arg, "__name__", None) in patterns for arg in sub_args]
        ):
            return True
        docs = docs[end + len(END) :].lstrip()
    return False


def call_if_exists(f, *args):
    global covered, analyses, current_file, session_id
    return_value = None
    for analysis in analyses:
        func = getattr(analysis, f, None)
        if func is not None and not filtered(func, f, args):
            return_value = func(*args)
            if covered is not None and len(args) >= 2:
                r_file, iid = args[0], args[1]
                if current_file is None or current_file.file_path != r_file:
                    current_file = IIDs(r_file)
                if r_file not in covered:
                    covered[r_file] = {}
                try:
                    line_no = current_file.iid_to_location[
                        iid
                    ].start_line  # This is not accurate for multiline statements like if, for, multiline calls, etc.
                    #               Also for exit control flow hooks, the entry would be marked as covered.
                except KeyError:
                    line_no = 0
                analysis_class_name = analysis.__class__.__name__
                if line_no not in covered[r_file]:
                    covered[r_file][line_no] = {analysis_class_name: 0}
                if analysis_class_name not in covered[r_file][line_no]:
                    covered[r_file][line_no][analysis_class_name] = 0
                covered[r_file][line_no][analysis_class_name] += 1
    return return_value


def _dynapyt_parse_to_ast_(code):
    return cst.parse_module(code)


def _write_(dyn_ast, iid, right, left):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("memory_access", dyn_ast, iid, right)
    new_left = left
    res = call_if_exists("write", dyn_ast, iid, new_left, right)
    if res is not None:
        return res
    return right


def _aug_assign_(dyn_ast, iid, left, opr, right):
    call_if_exists("runtime_event", dyn_ast, iid)
    operator = [
        "AddAssign",
        "BitAndAssign",
        "BitOrAssign",
        "BitXorAssign",
        "DivideAssign",
        "FloorDivideAssign",
        "LeftShiftAssign",
        "MatrixMultiplyAssign",
        "ModuloAssign",
        "MultiplyAssign",
        "PowerAssign",
        "RightShiftAssign",
        "SubtractAssign",
    ]
    call_if_exists("operation", dyn_ast, iid, operator[opr][:-6], [left, right], None)
    call_if_exists(
        "binary_operation", dyn_ast, iid, operator[opr][:-6], left, right, None
    )
    call_if_exists(snake(operator[opr][:-6]), dyn_ast, iid, left, right, None)
    eval_left = left()
    if opr == 0:
        new_val = eval_left + right
    elif opr == 1:
        new_val = eval_left & right
    elif opr == 2:
        new_val = eval_left | right
    elif opr == 3:
        new_val = eval_left ^ right
    elif opr == 4:
        new_val = eval_left / right
    elif opr == 5:
        new_val = eval_left // right
    elif opr == 6:
        new_val = eval_left << right
    elif opr == 7:
        new_val = eval_left @ right
    elif opr == 8:
        new_val = eval_left % right
    elif opr == 9:
        new_val = eval_left * right
    elif opr == 10:
        new_val = eval_left**right
    elif opr == 11:
        new_val = eval_left >> right
    elif opr == 12:
        new_val = eval_left - right
    call_if_exists("memory_access", dyn_ast, iid, new_val)
    call_if_exists("write", dyn_ast, iid, [left], new_val)
    result_high = call_if_exists(
        "augmented_assignment", dyn_ast, iid, left, operator[opr], right
    )
    result_low = call_if_exists(
        get_name(snake(operator[opr])), dyn_ast, iid, left, right
    )
    if result_low is not None:
        right = result_low
    elif result_high is not None:
        right = result_high
    return right


def _binary_op_(dyn_ast, iid, left, opr, right):
    call_if_exists("runtime_event", dyn_ast, iid)
    bin_op = [
        "Add",
        "BitAnd",
        "BitOr",
        "BitXor",
        "Divide",
        "FloorDivide",
        "LeftShift",
        "MatrixMultiply",
        "Modulo",
        "Multiply",
        "Power",
        "RightShift",
        "Subtract",
        "And",
        "Or",
    ]
    if opr < 13:
        try:
            left = left()
            right = right()
        except TypeError:
            raise
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
        result = left**right
    elif opr == 11:
        result = left >> right
    elif opr == 12:
        result = left - right
    elif opr == 13:
        try:
            left = left()
        except TypeError:
            raise
        if left:
            try:
                right = right()
            except TypeError:
                raise
            result = left and right
        else:
            result = left
    elif opr == 14:
        try:
            left = left()
        except TypeError:
            raise
        if left:
            result = left
        else:
            try:
                right = right()
            except TypeError:
                raise
            result = left or right
    call_if_exists("operation", dyn_ast, iid, bin_op[opr], [left, right], result)
    result_high = call_if_exists(
        "binary_operation", dyn_ast, iid, bin_op[opr], left, right, result
    )
    result_low = call_if_exists(
        get_name(snake(bin_op[opr])), dyn_ast, iid, left, right, result
    )
    if result_low is not None:
        return result_low
    elif result_high is not None:
        return result_high
    return result


def _unary_op_(dyn_ast, iid, opr, right):
    call_if_exists("runtime_event", dyn_ast, iid)
    un_op = ["BitInvert", "Minus", "Not", "Plus"]
    if opr == 0:
        result = ~right
    elif opr == 1:
        result = -right
    elif opr == 2:
        result = not right
    elif opr == 3:
        result = +right
    call_if_exists("operation", dyn_ast, iid, un_op[opr], [right], result)
    result_high = call_if_exists(
        "unary_operation", dyn_ast, iid, un_op[opr], right, result
    )
    result_low = call_if_exists(
        get_name(snake(un_op[opr])), dyn_ast, iid, right, result
    )
    if result_low is not None:
        return result_low
    elif result_high is not None:
        return result_high
    return result


def _comp_op_(dyn_ast, iid, left, comparisons):
    call_if_exists("runtime_event", dyn_ast, iid)
    comp_op = [
        "Equal",
        "GreaterThan",
        "GreaterThanEqual",
        "In",
        "Is",
        "LessThan",
        "LessThanEqual",
        "NotEqual",
        "IsNot",
        "NotIn",
    ]
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
        call_if_exists("operation", dyn_ast, iid, comp_op[op], [left, r], tmp)
        result_high = call_if_exists("comparison", dyn_ast, iid, l, comp_op[op], r, tmp)
        result_low = call_if_exists(
            get_name(snake(comp_op[op])), dyn_ast, iid, l, r, tmp
        )
        if result_low is not None:
            tmp = result_low
        elif result_high is not None:
            tmp = result_high
        result = result and tmp
        l = r
    return result


def _call_(dyn_ast, iid, call, only_post, pos_args, kw_args):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    if only_post:
        result = call
        new_res = call_if_exists(
            "post_call", dyn_ast, iid, result, call, pos_args, kw_args
        )
        return new_res if new_res is not None else result
    else:
        tmp = []
        for star, a in pos_args:
            if star == "":
                tmp.append(a)
            elif star == "*":
                tmp.extend(list(a))
            else:
                kw_args = dict(kw_args, **a)
        pos_args = tuple(tmp)
        call_if_exists("pre_call", dyn_ast, iid, call, pos_args, kw_args)
        result = call(*pos_args, **kw_args)
        new_res = call_if_exists(
            "post_call", dyn_ast, iid, result, call, pos_args, kw_args
        )
        return new_res if new_res is not None else result


def _bool_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("boolean", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _int_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("integer", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _float_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("float", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _str_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("string", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _img_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("imaginary", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _literal_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res = call_if_exists("literal", dyn_ast, iid, val)
    return res if res is not None else val


def _dict_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    value = dict()
    for v in val:
        if not isinstance(v, tuple):
            value.update(v)
        else:
            value.update({v[0]: v[1]})
    res_high = call_if_exists("literal", dyn_ast, iid, value)
    res_low = call_if_exists("dictionary", dyn_ast, iid, val, value)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return value


def _list_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("_list", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _tuple_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    value = tuple(val)
    call_if_exists("literal", dyn_ast, iid, value)
    res = call_if_exists("_tuple", dyn_ast, iid, val, value)
    return res if res is not None else value


def _set_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    value = set(val)
    call_if_exists("literal", dyn_ast, iid, value)
    res = call_if_exists("_set", dyn_ast, iid, val, value)
    return res if res is not None else value


def _none_(dyn_ast, iid, val):
    call_if_exists("runtime_event", dyn_ast, iid)
    res_high = call_if_exists("literal", dyn_ast, iid, val)
    res_low = call_if_exists("none", dyn_ast, iid, val)
    if res_low is not None:
        return res_low
    elif res_high is not None:
        return res_high
    return val


def _delete_(dyn_ast, iid, del_target: List[Tuple[Any, Any, bool]], analyze: bool):
    if analyze:
        call_if_exists("runtime_event", dyn_ast, iid)
        call_if_exists("memory_access", dyn_ast, iid, del_target)
        cancel = call_if_exists("delete", dyn_ast, iid, del_target)
    else:
        cancel = None
    if (cancel is not None) and (cancel == True):
        pass
    else:
        for dt in del_target:
            base, offset, is_sub = dt
            if is_sub:
                if len(offset) == 1:
                    base.__delitem__(offset[0])
                else:
                    base.__delitem__(slice(offset))
            else:
                delattr(base, offset)


def _attr_(dyn_ast, iid, base, attr):
    call_if_exists("runtime_event", dyn_ast, iid)
    if (attr.startswith("__")) and (not attr.endswith("__")):
        if type(base).__name__ == "type":
            parents = [base]
        else:
            parents = [type(base)]
        found = True
        while len(parents) > 0:
            found = True
            cur_par = parents.pop()
            try:
                cur_name = cur_par.__name__
                cur_name = cur_name.lstrip("_")
                val = getattr(base, "_" + cur_name + attr)
            except AttributeError:
                found = False
                parents.extend(list(cur_par.__bases__))
                continue
            break
        if not found:
            raise AttributeError()
    else:
        val = getattr(base, attr)
    call_if_exists("memory_access", dyn_ast, iid, val)
    call_if_exists("read", dyn_ast, iid, val)
    result = call_if_exists("read_attribute", dyn_ast, iid, base, attr, val)
    return result if result is not None else val


def _sub_(dyn_ast, iid, base, sl):
    call_if_exists("runtime_event", dyn_ast, iid)
    if len(sl) == 1:
        val = base[sl[0]]
    else:
        val = base[tuple(sl)]
    call_if_exists("memory_access", dyn_ast, iid, val)
    call_if_exists("read", dyn_ast, iid, val)
    result = call_if_exists("read_subscript", dyn_ast, iid, base, sl, val)
    return result if result is not None else val


def _try_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("enter_try", dyn_ast, iid)


def _end_try_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("clean_exit_try", dyn_ast, iid)


def _exc_(dyn_ast, iid, exc=None, name=None):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exception", dyn_ast, iid, exc, name)


def _raise_(dyn_ast, iid, exc=None, cause=None):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    res = call_if_exists("_raise", dyn_ast, iid, exc, cause)
    if res is not None:
        exc, cause = res
    if exc == None:
        raise
    else:
        if cause == None:
            raise exc
        else:
            raise exc from cause


def _catch_(exception):
    t, v, stack_trace = exc_info()
    call_if_exists("runtime_event", "", -1)
    call_if_exists("uncaught_exception", exception, stack_trace)
    raise exception


def _read_(dyn_ast, iid, var_arg):
    call_if_exists("runtime_event", dyn_ast, iid)
    value = var_arg()
    call_if_exists("memory_access", dyn_ast, iid, value)
    call_if_exists("read", dyn_ast, iid, value)
    result = call_if_exists("read_identifier", dyn_ast, iid, value)
    return result if result is not None else value


def _if_expr_(dyn_ast, iid, condition, true_val, false_val):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists("enter_control_flow", dyn_ast, iid, condition)
    result_low = call_if_exists("enter_if", dyn_ast, iid, condition)
    final_condition = condition
    if result_low is not None:
        final_condition = result_low
    elif result_high is not None:
        final_condition = result_high
    if final_condition:
        res = true_val()
    else:
        res = false_val()
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exit_control_flow", dyn_ast, iid)
    call_if_exists("exit_if", dyn_ast, iid)
    return res


def _func_entry_(dyn_ast, iid, args, name: str, is_lambda=False):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("function_enter", dyn_ast, iid, args, name, is_lambda)


def _func_exit_(dyn_ast, iid, name: str):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("function_exit", dyn_ast, iid, name, None)
    return


def _return_(dyn_ast, iid, function_iid, function_name, return_val=None):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists(
        "function_exit", dyn_ast, function_iid, function_name, return_val
    )
    result_low = call_if_exists(
        "_return", dyn_ast, iid, function_iid, function_name, return_val
    )  # return needs both its own iid and the function iid
    if result_low is not None:
        return result_low
    elif result_high is not None:
        return result_high
    return return_val


def _yield_(dyn_ast, iid, function_iid, function_name, return_val=None):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists(
        "function_exit", dyn_ast, function_iid, function_name, return_val
    )
    result_low = call_if_exists(
        "_yield", dyn_ast, iid, function_iid, function_name, return_val
    )
    if result_low is not None:
        return result_low
    elif result_high is not None:
        return result_high
    return return_val


def _assert_(dyn_ast, iid, test, msg):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result = call_if_exists("_assert", dyn_ast, iid, test, msg)
    return result if result is not None else test


def _lambda_(dyn_ast, iid, args, expr):
    _func_entry_(dyn_ast, iid, args, "lambda", True)
    res = expr()
    return _return_(dyn_ast, iid, iid, res)


def _break_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result = call_if_exists("_break", dyn_ast, iid)
    return result if result is not None else True


def _continue_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result = call_if_exists("_continue", dyn_ast, iid)
    return result if result is not None else True


def _enter_if_(dyn_ast, iid, condition):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists("enter_control_flow", dyn_ast, iid, condition)
    result_low = call_if_exists("enter_if", dyn_ast, iid, condition)
    final_condition = condition
    if result_low is not None:
        final_condition = result_low
    elif result_high is not None:
        final_condition = result_high
    return final_condition


def _exit_if_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exit_control_flow", dyn_ast, iid)
    call_if_exists("exit_if", dyn_ast, iid)


def _enter_while_(dyn_ast, iid, condition):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists("enter_control_flow", dyn_ast, iid, condition)
    result_low = call_if_exists("enter_while", dyn_ast, iid, condition)
    if result_low is not None:
        return result_low
    elif result_high is not None:
        return result_high
    return condition


def _exit_while_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exit_control_flow", dyn_ast, iid)
    call_if_exists("exit_while", dyn_ast, iid)


def _enter_for_(dyn_ast, iid, next_val, iterable):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    result_high = call_if_exists(
        "enter_control_flow", dyn_ast, iid, not isinstance(next_val, StopIteration)
    )
    result_low = call_if_exists("enter_for", dyn_ast, iid, next_val, iterable)
    if result_low is not None:
        return result_low
    elif result_high is not None:
        if result_high:
            return next_val
        raise StopIteration()
    return next_val


def _exit_for_(dyn_ast, iid):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exit_control_flow", dyn_ast, iid)
    call_if_exists("exit_for", dyn_ast, iid)


def _gen_(dyn_ast, iid, iterator):
    if iterator is None:
        return

    new_iter = iter(iterator)
    while True:
        try:
            it = next(new_iter)
            result = _enter_for_(dyn_ast, iid, it, iterator)
            if result is not None:
                yield result
            else:
                yield it
        except StopIteration as e:
            _enter_for_(dyn_ast, iid, e, iterator)
            _exit_for_(dyn_ast, iid)
            return

        

@contextmanager
def _enter_with_(dyn_ast, iid, ctx_manager_arg):
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("enter_with", dyn_ast, iid, ctx_manager_arg)
    is_suppressed = False
    ctx_manager = ctx_manager_arg
    return_value = ctx_manager.__enter__()

    try:
        yield return_value
    except Exception as e:
        is_suppressed = ctx_manager.__exit__(type(e), e, e.__traceback__)
        if not is_suppressed:
            call_if_exists("runtime_event", dyn_ast, iid)
            call_if_exists("control_flow_event", dyn_ast, iid)
            call_if_exists("exit_with", dyn_ast, iid, False, e)
            raise
    else:
        ctx_manager.__exit__(None, None, None)
        
    call_if_exists("runtime_event", dyn_ast, iid)
    call_if_exists("control_flow_event", dyn_ast, iid)
    call_if_exists("exit_with", dyn_ast, iid, is_suppressed, None)