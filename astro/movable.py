"""Superclass for objects that move around onscreen.
"""

import math

from astro.timekeeper import Timekeeper
from astro.util import magnitude

class Movable(Timekeeper):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.speedx = self.speedx_prev = 0
        self.speedy = self.speedy_prev = 0

    def initialize(self):
        if hasattr(self, 'max_speed') and hasattr(self, 'acceleration'):
            # Calsulate stopping distance
            self.stopping_distance = (self.max_speed ** 2) / (self.acceleration * 2)

    def place(self, screen, startx, starty, speedx=0, speedy=0):
        """Adds this object to the game at the specified location.

        Can optionally specify an initial speed. Also adds it to its sprite groups.

        Args:
            startx (int): The starting x-coordinate.
            starty (int): The starting y-coordinate.
            speedx (optional int): The starting horizontal speed. Defaults to 0.
            speedy (optional int): The starting vertical speed. Defaults to 0.
        """
        self._last_updated = None
        self.screen = screen
        self.screen_size = self.screen.screen_size
        self.x = self.screen.convert_prop_x(startx)
        self.y = self.screen.convert_prop_y(starty)
        self.speedx = speedx
        self.speedy = speedy

    def tick(self, now, elapsed):
        """Main function called by self.update() to update the sprite for each "tick" of the
        simulation.
        """
        self._update_velocity(elapsed)
        self.update_position(elapsed)

    @property
    def cur_speed(self):
        return magnitude(self.speedx, self.speedy)

    @property
    def momentum(self):
        if getattr(self, 'mass', None):
            return self.mass * self.speedx, self.mass * self.speedy
        else:
            return (None, None)

    @property
    def kinetic_energy(self):
        if getattr(self, 'mass', None):
            return 0.5 * self.mass * self.cur_speed ** 2
        else:
            return None

    @property
    def direction(self):
        return math.atan2(self.speedy, self.speedx)

    def update_position(self, elapsed):
        """Called each tick; updates the sprite's position based on its velocity.
        """

        self.x += elapsed * (self.speedx + self.speedx_prev) / 2
        self.y += elapsed * (self.speedy + self.speedy_prev) / 2

    def _update_velocity(self, elapsed):
        self.speedx_prev = self.speedx
        self.speedy_prev = self.speedy
        self.update_velocity(elapsed)
        if hasattr(self, 'max_speed'):
            self.clamp_speed()

    def update_velocity(self, elapsed):
        """Called each tick; updates the objects's velocity.

        This defaults to doing nothing, e.g. for passively floating objects or dumbfired
        projectiles that don't accelerate. Controlled by player input for friendly ships
        and AI for hostile ships.
        """
        if hasattr(self, 'move_behavior'):
            self.move_behavior.update_velocity(elapsed)

    def clamp_speed(self):
        # Clamp speed to within the object's maximum speed
        speed = self.cur_speed
        if abs(speed) > self.max_speed:
            self.speedx = self.speedx * self.max_speed / speed
            self.speedy = self.speedy * self.max_speed / speed

    def accelerate_toward(self, elapsed, targetx, targety):
        # Accelerate towards the target velocity
        # Requires self.acceleration and self.max_speed to be defined
        dx = targetx - self.speedx
        dy = targety - self.speedy
        dv = magnitude(dx, dy)
        if dv:
            max_accel = self.acceleration * elapsed
            if dv < max_accel:
                self.speedx, self.speedy = targetx, targety
            else:
                self.speedx += dx * max_accel / dv
                self.speedy += dy * max_accel / dv

    def accelerate_toward_point(self, elapsed, targetx, targety, decelerate=True):
        # Move towards the target point
        # Requires self.acceleration and self.max_speed to be defined
        dx = targetx - self.x
        dy = targety - self.y

        distance = magnitude(dx, dy)
        if distance:
            target_speed = self.max_speed
            if decelerate:
                target_speed *= min(1.0, distance / self.stopping_distance)
            target_speedx = dx * target_speed / distance
            target_speedy = dy * target_speed / distance

            return self.accelerate_toward(elapsed, target_speedx, target_speedy)

    def get_exit_point(self, x, y, vx, vy):
        """Finds where a Movable object will leave the screen.
        """

        x_bound = (self.screen_size[0] - x) if vx > 0 else -x
        y_bound = (self.screen_size[1] - y) if vy > 0 else -y
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

    def lead_target(self, x2, y2, vx2, vy2,
        projectile_speed, mode, relative_to_firer_velocity=True):
        """Finds the angle this ovbject has to move/shoot a projectile at to hit another Movable
        """

        x1, y1, vx1, vy1 = self.x, self.y, self.speedx, self.speedy
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
               collision_x < 0 or collision_x > self.screen_size[0] or \
               collision_y < 0 or collision_y > self.screen_size[1]:

                # Aim at where the player ship will hit the edge of the screen
                exit_x, exit_y = self.get_exit_point(x2, y2, vx2, vy2)
                angle = self.lead_target(exit_x, exit_y, 0, 0, projectile_speed, 1,
                    relative_to_firer_velocity)
                angle = math.atan2(exit_x - x1, exit_y - y1)

        return angle
