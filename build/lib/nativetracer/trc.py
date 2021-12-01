import opcode
def _trace_opcodes_(frame, event, arg=None):
    if event == 'opcode':
        code = frame.f_code
        offset = frame.f_lasti
        # print(f"{opcode.opname[code.co_code[offset]]:<18} | {frame.f_lineno}")
    else:
        #print('x')
        frame.f_trace_opcodes = True
    return _trace_opcodes_

def _trace_assignments_(frame, event, arg=None):
    if event == 'line':
        x = 0
        y = frame
    else:
        x = 1
        y = event
    z = x
    yy = y
    return _trace_assignments_