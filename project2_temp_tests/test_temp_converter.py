"""
Simple tests for temp_converter functions.

Run with:  pytest test_temp_converter.py
"""

from temp_converter import c_to_f, f_to_c


def test_freezing_point():
    assert c_to_f(0) == 32
    assert round(f_to_c(32), 6) == 0


def test_boiling_point():
    assert c_to_f(100) == 212
    assert round(f_to_c(212), 6) == 100


def test_random_value_round_trip():
    value_c = 37.5
    value_f = c_to_f(value_c)
    back_to_c = f_to_c(value_f)
    assert abs(back_to_c - value_c) < 1e-9


def test_raises_on_bad_input():
    import pytest

    with pytest.raises(TypeError):
        c_to_f("hot")  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        f_to_c(None)  # type: ignore[arg-type]
