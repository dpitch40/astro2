"""Superclass for objects that move around onscreen.
"""

import math

from astro.timekeeper import Timekeeper
from astro.util import magnitude, convert_prop_x, convert_prop_y

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

    def place(self, startx, starty, speedx=0, speedy=0):
        """Adds this object to the game at the specified location.

        Can optionally specify an initial speed. Also adds it to its sprite groups.

        Args:
            startx (int): The starting x-coordinate.
            starty (int): The starting y-coordinate.
            speedx (optional int): The starting horizontal speed. Defaults to 0.
            speedy (optional int): The starting vertical speed. Defaults to 0.
        """
        self.x = convert_prop_x(startx)
        self.y = convert_prop_y(starty)
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
