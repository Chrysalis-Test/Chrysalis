"""
A collection of simple but useful invariants.

In an attempt to reduce boiler plate code, we provide an ever-growing collection of
simple invariants. This module is designed to be imported in its totality so that each
invariant can be used by simply specifying an attribute of the module. This removes the
need of the user to define their own functions for these simple invaraints (especially
since we don't allow users to use lambda functions for invariants).

This collection can be added to as collaborators see fit. General guidelines for adding
a new invariant are as follows:
- The new invariant is general
- The new invariant is easy to understand at a moment's glance

Notes
-----
All invariants defined must be import in the `chrysalis/invariants.py` file.
Additionally, the function must have a docstring to be documented in the API reference.
"""


def equals[T](curr: T, prev: T) -> bool:
    """Check if current value equals previous value."""
    return curr == prev


def not_equals[T](curr: T, prev: T) -> bool:
    """Check if current value does not equal previous value."""
    return curr != prev


def is_same_sign(curr: float, prev: float) -> bool:
    """Check if current and previous values have the same sign."""
    return curr >= 0 and prev >= 0 or curr <= 0 and prev <= 0


def not_same_sign(curr: float, prev: float) -> bool:
    """Check if current and previous values have different signs."""
    return not is_same_sign(curr, prev)


def greater_than(curr: float, prev: float) -> bool:
    """Check if current value is greater than previous value."""
    return curr > prev


def greater_than_equal(curr: float, prev: float) -> bool:
    """Check if current value is greater than or equal to previous value."""
    return curr >= prev


def less_than(curr: float, prev: float) -> bool:
    """Check if current value is less than previous value."""
    return curr < prev


def less_than_equal(curr: float, prev: float) -> bool:
    """Check if current value is less than or equal to previous value."""
    return curr <= prev
