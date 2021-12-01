def _assign_(iid, left, right):
    if iid < 100:
        temp = 10
    else:
        temp = 20
    temp += iid
    res = right()
    return res

def _binary_op_(iid, left, opr, right, val):
    return val()

def _unary_op_(iid, opr, right, val):
    return val()