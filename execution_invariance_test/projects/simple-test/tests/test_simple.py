from simple_test.simple import add_one, multiply_two, add_together


def test_add_one_1():
    assert add_one(1) == 2


def test_add_one_2():
    assert add_one(2) == 3


def test_multiply_two_1():
    assert multiply_two(1) == 2


def test_multiply_two_2():
    assert multiply_two(2) == 4


def test_add_together_1_2():
    assert add_together(1, 2) == 3


def test_add_together_2_3():
    assert add_together(2, 3) == 5
