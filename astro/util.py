import math

from astro import SCREEN_SIZE

def convert_prop_x(x):
    return round(x * SCREEN_SIZE[0])

def convert_prop_y(y):
    return round(y * SCREEN_SIZE[1])

def convert_proportional_coordinates(x, y):
    return convert_prop_x(x), convert_prop_y(y)

def convert_proportional_coordinate_list(coords):
    """Converts a list of (x, y)-tuples from floats between 0 and 1 (proportions of the screen size)
       to pixel coordinates.
    """

    return [convert_proportional_coordinates(x, y) for x, y in coords]

def magnitude(x, y):
    return math.sqrt(x ** 2 + y ** 2)

def angle_distance(angle1, angle2):
    return min(abs(angle2 - angle1), abs(angle2 - angle1 - 360), abs(angle2 - angle1 + 360))

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
