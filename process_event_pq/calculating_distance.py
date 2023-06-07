from numba import njit, double
import math


AVG_RADIUS_PLANET = 6371
PI = 3.14


@njit(double(double))
def to_radian(value):
    return value * PI / 180


@njit(double(double, double, double, double))
def operate_distance(
    x1, # latitude
    y1, # longitude
    x2, # latitude
    y2  # longitude
):
    x1_r = to_radian(x1)
    y1_r = to_radian(y1)
    x2_r = to_radian(x2)
    y2_r = to_radian(y2)

    cos_d = math.sin(x1_r) * math.sin(x2_r) + math.cos(x1_r) * math.cos(x2_r) * math.cos(y1_r - y2_r)
    d = math.acos(cos_d)
    l = d * AVG_RADIUS_PLANET

    return l
