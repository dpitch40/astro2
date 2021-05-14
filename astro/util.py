import math

import pygame

from astro import SCREEN_SIZE

def magnitude(x, y):
    return math.sqrt(x ** 2 + y ** 2)

def angle_distance(angle1, angle2, radians=False):
    circle = 2 * math.pi if radians else 360
    return min(abs(angle2 - angle1), abs(angle2 - angle1 - circle), abs(angle2 - angle1 + circle))

def binary_search(f, lower, upper, threshold=0.00001, geometric_mean=False):
    mid = lower
    mid_val = f(lower)
    if mid_val > 0:
        lower, upper = upper, lower

    while abs(mid_val) > threshold:
        if geometric_mean:
            mid = math.sqrt(lower * upper)
        else:
            mid = (lower + upper) / 2
        mid_val = f(mid)
        if mid_val > 0:
            upper = mid
        else:
            lower = mid

    return mid

def frange(start, stop=None, step=None):
    """Floating-point version of range.
    """
    if stop is None:
        start, stop = 0.0, start
    if step is None:
        step = 1.0

    current = start
    while current < stop:
        yield current
        current += step
