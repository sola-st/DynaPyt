import json
from pathlib import Path
import importlib.util
import sys

module_name = "dynapyt.analyses.TraceAll"
spec = importlib.util.spec_from_file_location(
    module_name,
    Path(__file__).parent.resolve()
    / ".."
    / "src"
    / "dynapyt"
    / "analyses"
    / "TraceAll.py",
)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

hooks = dir(module.TraceAll())
hooks = [h for h in hooks if not h.startswith("__")]
hooks.remove("iid_to_location")
hooks.remove("asts")
hooks.remove("_get_ast")
hooks.remove("location_to_iid")
hooks.remove("log")
hooks.remove("conf")
hooks.remove("output_dir")
traceall_hooks = set(hooks)

with open(
    Path(__file__).parent.resolve()
    / ".."
    / "src"
    / "dynapyt"
    / "utils"
    / "hierarchy.json",
    "r",
) as f:
    hierarchy = json.load(f)

hierarchy_hooks = set()
q = [hierarchy]
while len(q) > 0:
    curr = q.pop()
    for k, v in curr.items():
        if len(v.items()) > 0:
            q.append(v)
        hierarchy_hooks.add(k)

non_matching = traceall_hooks.symmetric_difference(hierarchy_hooks)
if len(non_matching) > 0:
    raise Exception("Hooks do not match hierarchy", non_matching)


def to_string_list(root):
    if len(root.items()) == 0:
        return []
    res = []
    its = len(root.items())
    count = 0
    for k, v in root.items():
        count += 1
        if len(v.items()) > 0:
            res.append(f"└ [{k}](#TraceAll.{k})  ")
            inner_res = to_string_list(v)
            for i in range(len(inner_res)):
                inner_res[i] = (
                    ("│ " + "&nbsp; " * 3) if count < its else "&nbsp; " * 5
                ) + inner_res[i]
            res.extend(inner_res)
        else:
            res.append(f"└ [{k}](#TraceAll.{k})  ")
    return res


with open(Path(__file__).parent.resolve() / "hooks.md", "w") as f:
    # f.write("```\n" + "\n".join(to_string_list(hierarchy)) + "\n```\n")
    f.write("\n".join(to_string_list(hierarchy)) + "\n")
