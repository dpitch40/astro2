import math
import operator
import random

from astro.configurable import Configurable
from astro.util import magnitude, convert_proportional_coordinate_list, angle_distance, \
    convert_prop_x, convert_prop_y
from astro import ENEMIES, FRIENDLY_SHIPS, ENEMY_SHIPS, REACHED_DEST_THRESHOLD

class MoveBehavior(Configurable):
    defaults = {'initial_dest': None}

    def init_ship(self, ship):
        self.ship = ship

    def initialize(self):
        super().initialize()
        self.formation = None
        self.formation_i = None
        if self.initial_dest:
            self.pre_dest = self.initial_dest
        else:
            self.pre_dest = None

    def reached_dest(self, x, y):
        distance = magnitude(self.ship.x - x, self.ship.y - y)
        return distance < REACHED_DEST_THRESHOLD

    def update_velocity(self, elapsed):
        """Updates the parent ship's velocity.
        """

        if self.formation:
            # Let formation control movement
            self.formation.update_ship_velocity(elapsed, self.ship, self.formation_i)
        else:
            # Entry behavior
            if self.pre_dest:
                if not self.reached_dest(*self.pre_dest):
                    self.ship.accelerate_toward_point(elapsed, *self.pre_dest)
                else:
                    self.pre_dest = None
            else:
                self._update_velocity(elapsed)

    def _update_velocity(self, elapsed):
        pass

class Idle(MoveBehavior):
    def _update_velocity(self, elapsed):
        self.ship.accelerate_toward(elapsed, 0, 0)

class Patrol(MoveBehavior):
    """Causes the ship to move between a series of destinations.
    """

    required_fields = ()
    defaults = {'pause_time': 0}
    defaults.update(MoveBehavior.defaults)

    def initialize(self):
        super().initialize()
        self.pause_timer = self.pause_time
        self.cur_dest = None

    def _update_velocity(self, elapsed):
        if self.cur_dest is None:
            self.cur_dest = self.next_destination()

        if self.reached_dest(*self.cur_dest):
            if self.pause_timer is not None:
                self.pause_timer -= elapsed
                if self.pause_timer <= 0:
                    self.pause_timer = None

            if self.pause_timer is None:
                # Cycle to next destination
                self.cur_dest = self.next_destination()
                self.pause_timer = self.pause_time

        self.ship.accelerate_toward_point(elapsed, *self.cur_dest)

    def next_destination(self):
        """Chooses and returns the next destination.
        """
        raise NotImplemented

class FixedPatrol(Patrol):
    """Causes the ship to move between a list of destinations in a loop.
    """

    required_fields = ('dests',)
    defaults = {'pause_time': 0}
    defaults.update(MoveBehavior.defaults)

    def initialize(self):
        super().initialize()
        self._dests = convert_proportional_coordinate_list(self.dests)
        self.dest_i = 0

    def next_destination(self):
        dest = self._dests[self.dest_i]
        self.dest_i = (self.dest_i + 1) % len(self._dests)
        return dest

class RandomPatrol(Patrol):
    """Causes the ship to move to a series of random destinations..
    """

    required_fields = ('width', 'height')
    defaults = {'pause_time': 0}
    defaults.update(MoveBehavior.defaults)

    def initialize(self):
        super().initialize()
        width = convert_prop_x(self.width)
        self.max_x = convert_prop_x(0.5) + convert_prop_y(self.width) / 2
        self.min_x = convert_prop_x(0.5) - convert_prop_y(self.width) / 2
        self.max_y = convert_prop_y(self.height)

    def next_destination(self):
        return (random.randint(self.min_x, self.max_x), random.randint(0, self.max_y))

class Homing(MoveBehavior):
    defaults = {'target_acquisition_angle': 40}
    defaults.update(MoveBehavior.defaults)

    def __init__(self, key):
        super().__init__(key)

    def initialize(self):
        super().initialize()
        self.target = None

    def acquire_target(self):
        if set(self.ship.groups) & ENEMIES:
            target_group = FRIENDLY_SHIPS
        else:
            target_group = ENEMY_SHIPS

        if target_group and self.ship.speed:
            direction = self.ship.direction

            angles = sorted([(angle_distance(self.angle_to_target(s), direction, True), s)
                for s in target_group], key=operator.itemgetter(0))
            targets_ahead = [(a, s) for a, s in angles if a < math.radians(self.target_acquisition_angle / 2)]
            if targets_ahead:
                # Choose the closest target within the cone hat is
                # self.target_acquisition_angle degrees wide
                target_group = map(operator.itemgetter(1), targets_ahead)
            else:
                # Choose target closest to ahead
                self.target = angles[0][1]
                return

        if not target_group:
            self.target = None
        else:
            # Acquire based solely on distance
            key_func = lambda s: magnitude(self.ship.x - s.x, self.ship.y - s.y)
            self.target = sorted(target_group, key=key_func)[0]

    def angle_to_target(self, target):
        return math.atan2(target.y - self.ship.y, target.x - self.ship.x)

    def _update_velocity(self, elapsed):
        if self.target is None or not self.target.alive():
            self.acquire_target()
        
        if self.target is not None:
            self.ship.accelerate_toward_point(elapsed, self.target.x, self.target.y, decelerate=False)
