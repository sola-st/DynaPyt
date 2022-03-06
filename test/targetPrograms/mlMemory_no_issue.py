# DYNAPYT: DO NOT INSTRUMENT
# Used https://discuss.pytorch.org/t/high-memory-usage-while-training/162

from dynapyt.runtime import _catch_
from dynapyt.runtime import _int_, _aug_assign_, _read_, _write_, _gen_, _attr_, _unary_op_, _exit_for_, _sub_, _float_, _binary_op_, _call_

_dynapyt_ast_ = __file__ + ".orig"
try:
    import torch
    import torch.nn as nn
    from torch import optim
    
    class testNet(_attr_(_dynapyt_ast_, 0, nn, "Module")):
        def __init__(self):
            _call_(_dynapyt_ast_, 5, _attr_(_dynapyt_ast_, 4, _call_(_dynapyt_ast_, 3, super(_read_(_dynapyt_ast_, 1, lambda: testNet), _read_(_dynapyt_ast_, 2, lambda: self)), True, None, None), "__init__")(), True, None, None)
            self.rnn = _write_(_dynapyt_ast_, 11, _call_(_dynapyt_ast_, 10, _attr_(_dynapyt_ast_, 6, nn, "RNN"), False, [], {"input_size": _int_(_dynapyt_ast_, 7, 200), "hidden_size": _int_(_dynapyt_ast_, 8, 1000), "num_layers": _int_(_dynapyt_ast_, 9, 1)}), [lambda: self.rnn])
            self.linear = _write_(_dynapyt_ast_, 16, _call_(_dynapyt_ast_, 15, _attr_(_dynapyt_ast_, 12, nn, "Linear"), False, [("", _int_(_dynapyt_ast_, 13, 1000)), ("", _int_(_dynapyt_ast_, 14, 100))], {}), [lambda: self.linear])

        def forward(self, x, init):
            x = _write_(_dynapyt_ast_, 24, _sub_(_dynapyt_ast_, 23, _call_(_dynapyt_ast_, 21, _attr_(_dynapyt_ast_, 18, _read_(_dynapyt_ast_, 17, lambda: self), "rnn"), False, [("", _read_(_dynapyt_ast_, 19, lambda: x)), ("", _read_(_dynapyt_ast_, 20, lambda: init))], {}), [_int_(_dynapyt_ast_, 22, 0)]), [lambda: x])
            y = _write_(_dynapyt_ast_, 44, _call_(_dynapyt_ast_, 43, _attr_(_dynapyt_ast_, 26, _read_(_dynapyt_ast_, 25, lambda: self), "linear"), False, [("", _call_(_dynapyt_ast_, 42, _attr_(_dynapyt_ast_, 28, _read_(_dynapyt_ast_, 27, lambda: x), "view"), False, [("", _binary_op_(_dynapyt_ast_, 37, lambda: _call_(_dynapyt_ast_, 32, _attr_(_dynapyt_ast_, 30, _read_(_dynapyt_ast_, 29, lambda: x), "size"), False, [("", _int_(_dynapyt_ast_, 31, 0))], {}), 9, lambda: _call_(_dynapyt_ast_, 36, _attr_(_dynapyt_ast_, 34, _read_(_dynapyt_ast_, 33, lambda: x), "size"), False, [("", _int_(_dynapyt_ast_, 35, 1))], {}))), ("", _call_(_dynapyt_ast_, 41, _attr_(_dynapyt_ast_, 39, _read_(_dynapyt_ast_, 38, lambda: x), "size"), False, [("", _int_(_dynapyt_ast_, 40, 2))], {}))], {}))], {}), [lambda: y])
            return _call_(_dynapyt_ast_, 59, _attr_(_dynapyt_ast_, 46, _read_(_dynapyt_ast_, 45, lambda: y), "view"), False, [("", _call_(_dynapyt_ast_, 50, _attr_(_dynapyt_ast_, 48, _read_(_dynapyt_ast_, 47, lambda: x), "size"), False, [("", _int_(_dynapyt_ast_, 49, 0))], {})), ("", _call_(_dynapyt_ast_, 54, _attr_(_dynapyt_ast_, 52, _read_(_dynapyt_ast_, 51, lambda: x), "size"), False, [("", _int_(_dynapyt_ast_, 53, 1))], {})), ("", _call_(_dynapyt_ast_, 58, _attr_(_dynapyt_ast_, 56, _read_(_dynapyt_ast_, 55, lambda: y), "size"), False, [("", _int_(_dynapyt_ast_, 57, 1))], {}))], {})

    net = _write_(_dynapyt_ast_, 62, _call_(_dynapyt_ast_, 61, _read_(_dynapyt_ast_, 60, lambda: testNet), False, [], {}), [lambda: net])
    init = _write_(_dynapyt_ast_, 68, _call_(_dynapyt_ast_, 67, _attr_(_dynapyt_ast_, 63, torch, "zeros"), False, [("", _int_(_dynapyt_ast_, 64, 1)), ("", _int_(_dynapyt_ast_, 65, 4)), ("", _int_(_dynapyt_ast_, 66, 1000))], {}), [lambda: init])
    criterion = _write_(_dynapyt_ast_, 71, _call_(_dynapyt_ast_, 70, _attr_(_dynapyt_ast_, 69, nn, "CrossEntropyLoss"), False, [], {}), [lambda: criterion])
    optimizer = _write_(_dynapyt_ast_, 79, _call_(_dynapyt_ast_, 78, _attr_(_dynapyt_ast_, 72, optim, "SGD"), False, [("", _call_(_dynapyt_ast_, 75, _attr_(_dynapyt_ast_, 74, _read_(_dynapyt_ast_, 73, lambda: net), "parameters"), False, [], {}))], {"lr": _float_(_dynapyt_ast_, 76, 0.01), "momentum": _float_(_dynapyt_ast_, 77, 0.9)}), [lambda: optimizer])
    
    total_loss = _write_(_dynapyt_ast_, 81, _float_(_dynapyt_ast_, 80, 0.0), [lambda: total_loss])
    for i in _gen_(_dynapyt_ast_, 132, _call_(_dynapyt_ast_, 83, range(_int_(_dynapyt_ast_, 82, 10000)), True, None, None)): #10000 mini-batch
        input = _write_(_dynapyt_ast_, 89, _call_(_dynapyt_ast_, 88, _attr_(_dynapyt_ast_, 84, torch, "randn"), False, [("", _int_(_dynapyt_ast_, 85, 1000)), ("", _int_(_dynapyt_ast_, 86, 4)), ("", _int_(_dynapyt_ast_, 87, 200))], {}), [lambda: input]) #Seqlen = 1000, batch_size = 4, feature = 200
        target = _write_(_dynapyt_ast_, 96, _call_(_dynapyt_ast_, 95, _attr_(_dynapyt_ast_, 94, _call_(_dynapyt_ast_, 93, _attr_(_dynapyt_ast_, 90, torch, "LongTensor"), False, [("", _int_(_dynapyt_ast_, 91, 4)), ("", _int_(_dynapyt_ast_, 92, 1000))], {}), "zero_"), False, [], {}), [lambda: target])

        _call_(_dynapyt_ast_, 99, _attr_(_dynapyt_ast_, 98, _read_(_dynapyt_ast_, 97, lambda: optimizer), "zero_grad"), False, [], {})
        output = _write_(_dynapyt_ast_, 104, _call_(_dynapyt_ast_, 103, _read_(_dynapyt_ast_, 100, lambda: net), False, [("", _read_(_dynapyt_ast_, 101, lambda: input)), ("", _read_(_dynapyt_ast_, 102, lambda: init))], {}), [lambda: output])
        loss = _write_(_dynapyt_ast_, 121, _call_(_dynapyt_ast_, 120, _read_(_dynapyt_ast_, 105, lambda: criterion), False, [("", _call_(_dynapyt_ast_, 114, _attr_(_dynapyt_ast_, 107, _read_(_dynapyt_ast_, 106, lambda: output), "view"), False, [("", _unary_op_(_dynapyt_ast_, 109, 1, _int_(_dynapyt_ast_, 108, 1))), ("", _call_(_dynapyt_ast_, 113, _attr_(_dynapyt_ast_, 111, _read_(_dynapyt_ast_, 110, lambda: output), "size"), False, [("", _int_(_dynapyt_ast_, 112, 2))], {}))], {})), ("", _call_(_dynapyt_ast_, 119, _attr_(_dynapyt_ast_, 116, _read_(_dynapyt_ast_, 115, lambda: target), "view"), False, [("", _unary_op_(_dynapyt_ast_, 118, 1, _int_(_dynapyt_ast_, 117, 1)))], {}))], {}), [lambda: loss])
        _call_(_dynapyt_ast_, 124, _attr_(_dynapyt_ast_, 123, _read_(_dynapyt_ast_, 122, lambda: loss), "backward"), False, [], {})
        _call_(_dynapyt_ast_, 127, _attr_(_dynapyt_ast_, 126, _read_(_dynapyt_ast_, 125, lambda: optimizer), "step"), False, [], {})
        total_loss += _aug_assign_(_dynapyt_ast_, 131, lambda: total_loss, 0, _call_(_dynapyt_ast_, 130, _attr_(_dynapyt_ast_, 129, _read_(_dynapyt_ast_, 128, lambda: loss), "item"), False, [], {}))
    else:
        _exit_for_(_dynapyt_ast_, 132)
    
    _call_(_dynapyt_ast_, 134, print(_read_(_dynapyt_ast_, 133, lambda: total_loss)), True, None, None)
except Exception as _dynapyt_exception_:
    _catch_(_dynapyt_exception_)