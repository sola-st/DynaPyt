import importlib
from typing import List, Any
from ..analyses.BaseAnalysis import BaseAnalysis


def load_analyses(analyses: List[Any]) -> List[BaseAnalysis]:
    res_analyses = []
    for ana in analyses:
        if isinstance(ana, str):
            conf = None
            if ":" in ana:
                ana, conf = ana.split(":")
            module_parts = ana.split(".")
            module = importlib.import_module(".".join(module_parts[:-1]))
            class_ = getattr(module, module_parts[-1])
            if conf is not None:
                res_analyses.append(class_(conf))
            else:
                res_analyses.append(class_())
        elif isinstance(ana, BaseAnalysis):
            res_analyses.append(ana)
        else:
            continue
    return res_analyses
