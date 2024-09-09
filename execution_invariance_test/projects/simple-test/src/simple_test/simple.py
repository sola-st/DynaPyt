import traceback
import os.path

def add_one(x: int) -> int:
    return x + 1


def multiply_two(x: int) -> int:
    return x * 2


def add_together(x: int, y: int) -> int:
    return x + y


def get_stack():
    return traceback.extract_stack()