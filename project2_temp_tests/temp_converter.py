"""
Temperature conversion utilities for my remote-tech portfolio.
"""

from typing import Union

Number = Union[int, float]


def _validate_number(value: Number, name: str) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be an int or float, got {type(value).__name__}")
    return float(value)


def c_to_f(celsius: Number) -> float:
    """
    Convert temperature from Celsius to Fahrenheit.

    Formula: F = C * 9/5 + 32
    """
    c = _validate_number(celsius, "celsius")
    return c * 9.0 / 5.0 + 32.0


def f_to_c(fahrenheit: Number) -> float:
    """
    Convert temperature from Fahrenheit to Celsius.

    Formula: C = (F - 32) * 5/9
    """
    f = _validate_number(fahrenheit, "fahrenheit")
    return (f - 32.0) * 5.0 / 9.0
