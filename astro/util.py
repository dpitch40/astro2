import math

from astro import SCREEN_SIZE

def convert_proportional_coordinates(x, y):
    return round(x * SCREEN_SIZE[0]), round(y * SCREEN_SIZE[1])

def convert_proportional_coordinate_list(coords):
    """Converts a list of (x, y)-tuples from floats between 0 and 1 (proportions of the screen size)
       to pixel coordinates.
    """

    return [convert_proportional_coordinates(x, y) for x, y in coords]

def magnitude(x, y):
    return math.sqrt(x ** 2 + y ** 2)
