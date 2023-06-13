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
            res.append(k)
            res.extend(to_string_list(v))
        else:
            res.append(k)
    return res


with open(Path(__file__).parent.resolve() / "hooks.md", "w") as f:
    f.write("\n\n".join(to_string_list(hierarchy)) + "\n")
