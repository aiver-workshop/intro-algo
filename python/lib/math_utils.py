from decimal import Decimal


def to_nearest(num, tick_size: float):
    """Given a number, round it to the nearest tick. Very useful for sussing float error
       out of numbers: e.g. to_nearest(401.46, 0.01) -> 401.46, whereas processing is
       normally with floats would give you 401.46000000000004.
       Use this after adding/subtracting/multiplying numbers."""
    tick_dec = Decimal(str(tick_size))
    return float((Decimal(round(num / tick_size, 0)) * tick_dec))


def to_nearest_int(num, tick_size: float):
    """Given a number, round it to the nearest tick. Very useful for sussing float error
       out of numbers: e.g. to_nearest(401.46, 0.01) -> 401.46, whereas processing is
       normally with floats would give you 401.46000000000004.
       Use this after adding/subtracting/multiplying numbers."""
    tick_dec = Decimal(str(tick_size))
    return int((Decimal(round(num / tick_size, 0)) * tick_dec))