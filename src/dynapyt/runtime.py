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
from tempfile import gettempdir
from .utils.hooks import snake, get_name
from .instrument.IIDs import IIDs
from .instrument.filters import START, END, SEPERATOR
from .utils.runtimeUtils import load_analyses


class RuntimeEngine:
    _rt_engine = None

    def __new__(cls):
        if not cls._rt_engine:
            cls._rt_engine = super(RuntimeEngine, cls).__new__(cls)
            cls._rt_engine.__initialized = False
        return cls._rt_engine

    def __init__(self):
        if self.__initialized:
            return
        self.analyses = None
        self.covered = None
        self.coverage_path = None
        self.current_file = None
        self.end_execution_called = False
        self.engine_id = str(uuid.uuid4())
        self.session_id = os.environ.get("DYNAPYT_SESSION_ID", None)
        if self.session_id is None:
            os.environ["DYNAPYT_SESSION_ID"] = self.session_id = str(uuid.uuid4())
        self.analyses_file = (
            Path(gettempdir()) / f"dynapyt_analyses-{self.session_id}.txt"
        )
        self.set_analysis()
        self.set_coverage(os.environ.get("DYNAPYT_COVERAGE", None))
        self.__initialized = True

    def __del__(self):
        self.end_execution()

    def end_execution(self):
        if self.end_execution_called:
            return
        self.end_execution_called = True
        self.call_if_exists("end_execution")
        if self.covered is not None:
            with open(str(self.coverage_path), "w") as f:
                json.dump(self.covered, f)
        RuntimeEngine._rt_engine = None
        self.__initialized = False

    def set_analysis(self):
        self.analyses = []
        signal.signal(signal.SIGINT, self.end_execution)
        signal.signal(signal.SIGTERM, self.end_execution)
        atexit.register(self.end_execution)
        if self.analyses_file.exists():
            with open(str(self.analyses_file), "r") as af:
                new_analyses = af.read().strip().split("\n")
        else:
            raise Exception(f"Analyses file not found: {str(self.analyses_file)}")
        self.analyses = load_analyses(new_analyses)
        for analysis in self.analyses:
            if hasattr(analysis, "begin_execution"):
                analysis.begin_execution()

    def set_coverage(self, coverage_dir: str):
        print(f"Setting coverage for {coverage_dir}", file=sys.stderr)
        if coverage_dir is not None:
            coverage_dir = Path(coverage_dir)
            self.covered = {}
            coverage_dir.mkdir(exist_ok=True)
            self.coverage_path = coverage_dir / f"coverage-{self.engine_id}.json"
            if self.coverage_path.exists():
                self.coverage_path.unlink()

    def filtered(self, func, f, args):
        docs = func.__doc__
        if docs is None or START not in docs:
            return False
        if len(args) >= 2:
            sub_args = args[2:]
        else:
            return False
        sub_arg_names = []
        for arg in sub_args:
            if arg == () or arg == [] or arg == {}:
                continue
            if type(arg) == tuple and len(arg) == 1:
                arg = arg[0]
            try:
                name = arg.__dict__.get("__name__", None)
                if name is not None:
                    sub_arg_names.append(name)
                    continue
                else:
                    no_dict = True
            except AttributeError:
                no_dict = True
            try:
                sub_arg_names.append(arg.__name__)
                continue
            except AttributeError:
                no_name = True
            if no_dict and no_name:
                sub_arg_names.append(str(arg))
        if (
            func.__name__ == "post_call"
            and sub_args[0] == sub_args[1]
            and type(sub_args[0]) == super
        ):
            sub_arg_names.append("super")
        return_value = False
        while START in docs:
            start = docs.find(START)
            end = docs.find(END)
            fltr = docs[start + len(START) : end].strip()
            patterns = fltr.split(" -> ")[1].split(SEPERATOR)
            if fltr.startswith("only ->"):
                return_value = True
                if any([arg in patterns for arg in sub_arg_names]):
                    return False
            elif fltr.startswith("ignore ->"):
                return_value = False
                if any([arg in patterns for arg in sub_arg_names]):
                    return True
            docs = docs[end + len(END) :].lstrip()
        return return_value

    def call_if_exists(self, f, *args):
        return_value = None
        for analysis in self.analyses:
            func = getattr(analysis, f, None)
            if func is not None and not self.filtered(func, f, args):
                return_value = func(*args)
                if self.covered is not None and len(args) >= 2:
                    r_file, iid = args[0], args[1]
                    if (
                        self.current_file is None
                        or self.current_file.file_path != r_file
                    ):
                        self.current_file = IIDs(r_file)
                    if r_file not in self.covered:
                        self.covered[r_file] = {}
                    try:
                        line_no = self.current_file.iid_to_location[
                            iid
                        ].start_line  # This is not accurate for multiline statements like if, for, multiline calls, etc.
                        #               Also for exit control flow hooks, the entry would be marked as covered.
                    except KeyError:
                        line_no = 0
                    analysis_class_name = analysis.__class__.__name__
                    if line_no not in self.covered[r_file]:
                        self.covered[r_file][line_no] = {analysis_class_name: 0}
                    if analysis_class_name not in self.covered[r_file][line_no]:
                        self.covered[r_file][line_no][analysis_class_name] = 0
                    self.covered[r_file][line_no][analysis_class_name] += 1
        return return_value

    def _write_(self, dyn_ast, iid, right, left):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("memory_access", dyn_ast, iid, right)
        new_left = left
        res = self.call_if_exists("write", dyn_ast, iid, new_left, right)
        if res is not None:
            return res
        return right

    def _aug_assign_(self, dyn_ast, iid, left, opr, right):
        self.call_if_exists("runtime_event", dyn_ast, iid)
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
        self.call_if_exists(
            "operation", dyn_ast, iid, operator[opr][:-6], [left, right], None
        )
        self.call_if_exists(
            "binary_operation", dyn_ast, iid, operator[opr][:-6], left, right, None
        )
        self.call_if_exists(snake(operator[opr][:-6]), dyn_ast, iid, left, right, None)
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
        self.call_if_exists("memory_access", dyn_ast, iid, new_val)
        self.call_if_exists("write", dyn_ast, iid, [left], new_val)
        result_high = self.call_if_exists(
            "augmented_assignment", dyn_ast, iid, left, operator[opr], right
        )
        result_low = self.call_if_exists(
            get_name(snake(operator[opr])), dyn_ast, iid, left, right
        )
        if result_low is not None:
            right = result_low
        elif result_high is not None:
            right = result_high
        return right

    def _binary_op_(self, dyn_ast, iid, left, opr, right):
        self.call_if_exists("runtime_event", dyn_ast, iid)
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
        self.call_if_exists(
            "operation", dyn_ast, iid, bin_op[opr], [left, right], result
        )
        result_high = self.call_if_exists(
            "binary_operation", dyn_ast, iid, bin_op[opr], left, right, result
        )
        result_low = self.call_if_exists(
            get_name(snake(bin_op[opr])), dyn_ast, iid, left, right, result
        )
        if result_low is not None:
            return result_low
        elif result_high is not None:
            return result_high
        return result

    def _unary_op_(self, dyn_ast, iid, opr, right):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        un_op = ["BitInvert", "Minus", "Not", "Plus"]
        if opr == 0:
            result = ~right
        elif opr == 1:
            result = -right
        elif opr == 2:
            result = not right
        elif opr == 3:
            result = +right
        self.call_if_exists("operation", dyn_ast, iid, un_op[opr], [right], result)
        result_high = self.call_if_exists(
            "unary_operation", dyn_ast, iid, un_op[opr], right, result
        )
        result_low = self.call_if_exists(
            get_name(snake(un_op[opr])), dyn_ast, iid, right, result
        )
        if result_low is not None:
            return result_low
        elif result_high is not None:
            return result_high
        return result

    def _comp_op_(self, dyn_ast, iid, left, comparisons):
        self.call_if_exists("runtime_event", dyn_ast, iid)
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
            self.call_if_exists("operation", dyn_ast, iid, comp_op[op], [left, r], tmp)
            result_high = self.call_if_exists(
                "comparison", dyn_ast, iid, l, comp_op[op], r, tmp
            )
            result_low = self.call_if_exists(
                get_name(snake(comp_op[op])), dyn_ast, iid, l, r, tmp
            )
            if result_low is not None:
                tmp = result_low
            elif result_high is not None:
                tmp = result_high
            result = result and tmp
            l = r
        return result

    def _call_(self, dyn_ast, iid, call, only_post, pos_args, kw_args):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        if only_post:
            result = call
            new_res = self.call_if_exists(
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
            self.call_if_exists("pre_call", dyn_ast, iid, call, pos_args, kw_args)
            result = call(*pos_args, **kw_args)
            new_res = self.call_if_exists(
                "post_call", dyn_ast, iid, result, call, pos_args, kw_args
            )
            return new_res if new_res is not None else result

    def _bool_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("boolean", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _int_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("integer", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _float_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("float", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _str_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("string", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _img_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("imaginary", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _literal_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res = self.call_if_exists("literal", dyn_ast, iid, val)
        return res if res is not None else val

    def _dict_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        value = dict()
        for v in val:
            if not isinstance(v, tuple):
                value.update(v)
            else:
                value.update({v[0]: v[1]})
        res_high = self.call_if_exists("literal", dyn_ast, iid, value)
        res_low = self.call_if_exists("dictionary", dyn_ast, iid, val, value)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return value

    def _list_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("_list", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _tuple_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        value = tuple(val)
        self.call_if_exists("literal", dyn_ast, iid, value)
        res = self.call_if_exists("_tuple", dyn_ast, iid, val, value)
        return res if res is not None else value

    def _set_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        value = set(val)
        self.call_if_exists("literal", dyn_ast, iid, value)
        res = self.call_if_exists("_set", dyn_ast, iid, val, value)
        return res if res is not None else value

    def _none_(self, dyn_ast, iid, val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        res_high = self.call_if_exists("literal", dyn_ast, iid, val)
        res_low = self.call_if_exists("none", dyn_ast, iid, val)
        if res_low is not None:
            return res_low
        elif res_high is not None:
            return res_high
        return val

    def _delete_(
        self, dyn_ast, iid, del_target: List[Tuple[Any, Any, bool]], analyze: bool
    ):
        if analyze:
            self.call_if_exists("runtime_event", dyn_ast, iid)
            self.call_if_exists("memory_access", dyn_ast, iid, del_target)
            cancel = self.call_if_exists("delete", dyn_ast, iid, del_target)
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

    def _attr_(self, dyn_ast, iid, base, attr):
        self.call_if_exists("runtime_event", dyn_ast, iid)
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
            if attr in ["__getattribute__", "__getattr__"]:
                return val
        self.call_if_exists("memory_access", dyn_ast, iid, val)
        self.call_if_exists("read", dyn_ast, iid, val)
        result = self.call_if_exists("read_attribute", dyn_ast, iid, base, attr, val)
        return result if result is not None else val

    def _sub_(self, dyn_ast, iid, base, sl):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        if len(sl) == 1:
            val = base[sl[0]]
        else:
            val = base[tuple(sl)]
        self.call_if_exists("memory_access", dyn_ast, iid, val)
        self.call_if_exists("read", dyn_ast, iid, val)
        result = self.call_if_exists("read_subscript", dyn_ast, iid, base, sl, val)
        return result if result is not None else val

    def _try_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("enter_try", dyn_ast, iid)

    def _end_try_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("clean_exit_try", dyn_ast, iid)

    def _exc_(self, dyn_ast, iid, exc=None, name=None):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exception", dyn_ast, iid, exc, name)

    def _raise_(self, dyn_ast, iid, exc=None, cause=None):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        res = self.call_if_exists("_raise", dyn_ast, iid, exc, cause)
        if res is not None:
            exc, cause = res
        if exc == None:
            raise
        else:
            if cause == None:
                raise exc
            else:
                raise exc from cause

    def _catch_(self, exception):
        t, v, stack_trace = exc_info()
        self.call_if_exists("runtime_event", "", -1)
        self.call_if_exists("uncaught_exception", exception, stack_trace)
        self.end_execution()
        raise exception

    def _read_(self, dyn_ast, iid, var_arg):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        value = var_arg()
        self.call_if_exists("memory_access", dyn_ast, iid, value)
        self.call_if_exists("read", dyn_ast, iid, value)
        result = self.call_if_exists("read_identifier", dyn_ast, iid, value)
        return result if result is not None else value

    def _if_expr_(self, dyn_ast, iid, condition, true_val, false_val):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists("enter_control_flow", dyn_ast, iid, condition)
        result_low = self.call_if_exists("enter_if", dyn_ast, iid, condition)
        final_condition = condition
        if result_low is not None:
            final_condition = result_low
        elif result_high is not None:
            final_condition = result_high
        if final_condition:
            res = true_val()
        else:
            res = false_val()
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exit_control_flow", dyn_ast, iid)
        self.call_if_exists("exit_if", dyn_ast, iid)
        return res

    def _func_entry_(self, dyn_ast, iid, args, name: str, is_lambda=False):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("function_enter", dyn_ast, iid, args, name, is_lambda)

    def _func_exit_(self, dyn_ast, iid, name: str):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("function_exit", dyn_ast, iid, name, None)
        return

    def _return_(self, dyn_ast, iid, function_iid, function_name, return_val=None):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists(
            "function_exit", dyn_ast, function_iid, function_name, return_val
        )
        result_low = self.call_if_exists(
            "_return", dyn_ast, iid, function_iid, function_name, return_val
        )  # return needs both its own iid and the function iid
        if result_low is not None:
            return result_low
        elif result_high is not None:
            return result_high
        return return_val

    def _yield_(self, dyn_ast, iid, function_iid, function_name, return_val=None):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists(
            "function_exit", dyn_ast, function_iid, function_name, return_val
        )
        result_low = self.call_if_exists(
            "_yield", dyn_ast, iid, function_iid, function_name, return_val
        )
        if result_low is not None:
            return result_low
        elif result_high is not None:
            return result_high
        return return_val

    def _assert_(self, dyn_ast, iid, test, msg):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result = self.call_if_exists("_assert", dyn_ast, iid, test, msg)
        return result if result is not None else test

    def _lambda_(self, dyn_ast, iid, args, expr):
        self._func_entry_(dyn_ast, iid, args, "lambda", True)
        res = expr()
        return self._return_(dyn_ast, iid, iid, res)

    def _break_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result = self.call_if_exists("_break", dyn_ast, iid)
        return result if result is not None else True

    def _continue_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result = self.call_if_exists("_continue", dyn_ast, iid)
        return result if result is not None else True

    def _enter_if_(self, dyn_ast, iid, condition):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists("enter_control_flow", dyn_ast, iid, condition)
        result_low = self.call_if_exists("enter_if", dyn_ast, iid, condition)
        final_condition = condition
        if result_low is not None:
            final_condition = result_low
        elif result_high is not None:
            final_condition = result_high
        return final_condition

    def _exit_if_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exit_control_flow", dyn_ast, iid)
        self.call_if_exists("exit_if", dyn_ast, iid)

    def _enter_while_(self, dyn_ast, iid, condition):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists("enter_control_flow", dyn_ast, iid, condition)
        result_low = self.call_if_exists("enter_while", dyn_ast, iid, condition)
        if result_low is not None:
            return result_low
        elif result_high is not None:
            return result_high
        return condition

    def _exit_while_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exit_control_flow", dyn_ast, iid)
        self.call_if_exists("exit_while", dyn_ast, iid)

    def _enter_for_(self, dyn_ast, iid, next_val, iterable):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        result_high = self.call_if_exists(
            "enter_control_flow", dyn_ast, iid, not isinstance(next_val, StopIteration)
        )
        result_low = self.call_if_exists("enter_for", dyn_ast, iid, next_val, iterable)
        if result_low is not None:
            return result_low
        elif result_high is not None:
            if result_high:
                return next_val
            raise StopIteration()
        return next_val

    def _exit_for_(self, dyn_ast, iid):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exit_control_flow", dyn_ast, iid)
        self.call_if_exists("exit_for", dyn_ast, iid)

    def _gen_(self, dyn_ast, iid, iterator):
        if iterator is None:
            return

        new_iter = iter(iterator)
        while True:
            try:
                it = next(new_iter)
                result = self._enter_for_(dyn_ast, iid, it, iterator)
                if result is not None:
                    yield result
                else:
                    yield it
            except StopIteration as e:
                self._enter_for_(dyn_ast, iid, e, iterator)
                self._exit_for_(dyn_ast, iid)
                return

    @contextmanager
    def _enter_with_(self, dyn_ast, iid, ctx_manager_arg):
        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("enter_with", dyn_ast, iid, ctx_manager_arg)
        is_suppressed = False
        ctx_manager = ctx_manager_arg
        return_value = ctx_manager.__enter__()

        try:
            yield return_value
        except Exception as e:
            is_suppressed = ctx_manager.__exit__(type(e), e, e.__traceback__)
            if not is_suppressed:
                self.call_if_exists("runtime_event", dyn_ast, iid)
                self.call_if_exists("control_flow_event", dyn_ast, iid)
                self.call_if_exists("exit_with", dyn_ast, iid, False, e)
                raise
        else:
            ctx_manager.__exit__(None, None, None)

        self.call_if_exists("runtime_event", dyn_ast, iid)
        self.call_if_exists("control_flow_event", dyn_ast, iid)
        self.call_if_exists("exit_with", dyn_ast, iid, is_suppressed, None)
