import traceback
from simple_test.simple import get_stack

def test_stack():
    trace = get_stack()
    trace_list = traceback.format_list(trace)
    trace_length = len(trace_list)
    expected_trace_str_length = 34
    assert trace_length == expected_trace_str_length

