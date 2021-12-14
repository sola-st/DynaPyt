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
        print(dir(frame))
        print(dir(frame.f_code))
        print(frame.f_globals)
        print(frame.f_lasti)
        print(frame.f_lineno)
        print(frame.f_locals)
        for i in dir(frame.f_code):
            if i.startswith('co_'):
                print(i, getattr(frame.f_code, i))
        x = 0
        y = frame
    else:
        x = 1
        y = event
    z = x
    yy = y
    return _trace_assignments_

def _trace_all_(frame, event, arg=None):
    print(event)
    print(dir(frame))
    print(dir(frame.f_code))
    print(frame.f_globals)
    print(frame.f_lasti)
    print(frame.f_lineno)
    print(frame.f_locals)
    for i in dir(frame.f_code):
        if i.startswith('co_'):
            print(i, getattr(frame.f_code, i))
    return _trace_all_