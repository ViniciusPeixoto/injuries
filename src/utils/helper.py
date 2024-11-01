from math import pi
from typing import Union

from pandas import DataFrame


def angle_to_rad(angle: Union[float, DataFrame]) -> float:
    """
    Convert and `angle` from degrees to radians.
    """
    return angle * (pi / 180)
