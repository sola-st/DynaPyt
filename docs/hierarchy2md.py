import json
from pathlib import Path

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


def to_string_list(root):
    if len(root.items()) == 0:
        return []
    res = []
    for k, v in root.items():
        if len(v.items()) > 0:
            res.append("└ " + k)
            inner_res = to_string_list(v)
            for i in range(len(inner_res)):
                inner_res[i] = "│ " + inner_res[i]
            res.extend(inner_res)
        else:
            res.append("└ " + k)
    return res


with open(Path(__file__).parent.resolve() / "hooks.md", "w") as f:
    f.write("```bash\n" + "\n".join(to_string_list(hierarchy)) + "\n```\n")
