"""
Helper functions useful when writing analyses.
"""

from typing import Callable, NewType

UndefinedValueType = NewType("UndefinedValueType", str)
undefined_value = UndefinedValueType("undefined_value")


def get_old_value(value_as_lambda: Callable) -> bool:
    """
    Given a lambda function that represents an old value (just before a write),
    return the value or the special value `undefined_value`.
    """
    try:
        v = value_as_lambda()
        return v
    except (NameError, KeyError):
        return undefined_value
