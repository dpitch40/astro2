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

def get_exit_point(x, y, vx, vy):
    """Finds where a Movable object will leave the screen.
    """

    x_bound = (SCREEN_SIZE[0] - x) if vx > 0 else -x
    y_bound = (SCREEN_SIZE[1] - y) if vy > 0 else -y
    if vx != 0:
        if vy != 0:
            exit_time = min(x_bound / vx, y_bound / vy)
        else:
            exit_time = x_bound / vx
    elif vy != 0:
        exit_time = y_bound / vy
    else:
        exit_time = None

    if exit_time is not None:
        return x + vx * exit_time, y + vy * exit_time
    else:
        # Last resport: return current position
        return x, y

def lead_target(x1, y1, x2, y2, vx1, vy1, vx2, vy2,
    projectile_speed, mode, relative_to_firer_velocity=True):
    """Finds the angle obj1 has to shoot a projectile at to hit obj2
    """

    mode = 2
    dx = x2 - x1
    dy = y2 - y1
    d = magnitude(dx, dy)
    phi = math.atan2(dx, dy)

    dxprime = dyprime = 0
    if mode > 0:
        if relative_to_firer_velocity:
            # Compensate for the firing ship's velocity
            dxprime += vx1
            dyprime += vy1
        if mode == 2:
            # Compensate for both ship's velocity (lead the target)
            dxprime -= vx2
            dyprime -= vy2

    a = (dy * dxprime - dx * dyprime) / (d * projectile_speed)
    if a > 1:
        a = 1
    elif a < -1:
        a = -1
    angle = phi - math.asin(a)

    if mode == 2 and (vx2 or vy2):
        proj_speedx = projectile_speed * math.sin(angle)
        if relative_to_firer_velocity:
            proj_speedx += vx1
        proj_speedy = projectile_speed * math.cos(angle)
        if relative_to_firer_velocity:
            proj_speedy += vy1

        if proj_speedx - vx2 > 0:
            collision_time = (x2 - x1) / (proj_speedx - vx2)
        else:
            collision_time = (y2 - y1) / (proj_speedy - vy2)

        # Calculate where the shot will hit the target
        collision_x = x1 + proj_speedx * collision_time
        collision_y = y1 + proj_speedy * collision_time

        if collision_time < 0 or collision_time > 10 or \
           collision_x < 0 or collision_x > SCREEN_SIZE[0] or \
           collision_y < 0 or collision_y > SCREEN_SIZE[1]:

            # Aim at where the player ship will hit the edge of the screen
            exit_x, exit_y = get_exit_point(x2, y2, vx2, vy2)
            angle = lead_target(x1, y1, exit_x, exit_y, vx1, vy1, 0, 0, projectile_speed, 1,
                relative_to_firer_velocity)
            angle = math.atan2(exit_x - x1, exit_y - y1)

    return angle
