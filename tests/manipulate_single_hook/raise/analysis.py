from typing import Any, Optional
from dynapyt.analyses.BaseAnalysis import BaseAnalysis


class TestAnalysis(BaseAnalysis):
    def _raise(self, dyn_ast: str, iid: int, exc: Exception, cause: Any) -> Optional[Exception]:
        print(f"Exception with message {exc} and cause with message {cause}")
        if type(exc) == KeyError:
            return TypeError()