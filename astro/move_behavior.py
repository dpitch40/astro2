import math
import operator
import random

from astro.configurable import Configurable
from astro.util import magnitude, angle_distance
from astro import ENEMIES, FRIENDLY_SHIPS, ENEMY_SHIPS, REACHED_DEST_THRESHOLD

class MoveBehavior(Configurable):
    defaults = {'initial_dest': None}

    def init_ship(self, ship):
        self.ship = ship
        if self.initial_dest:
            self.initial_dest = self.ship.screen.convert_proportional_coordinates(*self.initial_dest)
            self.pre_dest = self.initial_dest
        else:
            self.pre_dest = None

    def initialize(self):
        super().initialize()
        self.formation = None
        self.formation_i = None

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
                    self._update_velocity(elapsed)
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

    def init_ship(self, ship):
        super().init_ship(ship)
        self._dests = self.ship.screen.convert_proportional_coordinate_list(self.dests)
        self.dest_i = 0

    def next_destination(self):
        dest = self._dests[self.dest_i]
        self.dest_i = (self.dest_i + 1) % len(self._dests)
        return dest

class RandomPatrol(Patrol):
    """Causes the ship to move to a series of random destinations.

    Arguments:
        width: Width of the "box" that the ship will randomly travel within, centered on the center
            of the screen.
        height: Height of the "box" the ship will randomly travel within, starting from the top of the
            screen.
    """

    required_fields = ('width', 'height')
    defaults = {'pause_time': 0}
    defaults.update(MoveBehavior.defaults)

    def init_ship(self, ship):
        super().init_ship(ship)
        self.width = self.ship.screen.convert_prop_x(self.width)
        self.height = self.ship.screen.convert_prop_y(self.height)
        self.max_x = self.ship.screen.convert_prop_x(0.5) + self.ship.screen.convert_prop_x(self.width) // 2
        self.min_x = self.ship.screen.convert_prop_x(0.5) - self.ship.screen.convert_prop_x(self.width) // 2
        self.min_y = self.ship.screen.convert_prop_y(0.0)
        self.max_y = self.height

    def next_destination(self):
        dest = (random.randint(self.min_x, self.max_x), random.randint(self.min_y, self.max_y))
        return dest

class Homing(MoveBehavior):
    defaults = {'target_acquisition_angle': 40}
    defaults.update(MoveBehavior.defaults)

    def __init__(self, key):
        super().__init__(key)

    def initialize(self):
        super().initialize()
        self.target = None

    def acquire_target(self):
        target_group = self.get_target_group()
        if not target_group:
            self.target = None
        else:
            self.target = self.choose_target(target_group)

    def get_target_group(self):
        if self.ship in ENEMIES:
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
                target_group = list(map(operator.itemgetter(1), targets_ahead))
            else:
                # Choose target closest to ahead
                return [angles[0][1]]
        return target_group


    def choose_target(self, target_group):
        # Acquire based solely on distance
        key_func = lambda s: magnitude(self.ship.x - s.x, self.ship.y - s.y)
        return sorted(target_group, key=key_func)[0]

    def angle_to_target(self, target):
        return math.atan2(target.y - self.ship.y, target.x - self.ship.x)

    def _update_velocity(self, elapsed):
        if self.target is None or not self.target.alive():
            self.acquire_target()
        
        if self.target is not None:
            self.ship.accelerate_toward_point(elapsed, self.target.x, self.target.y, decelerate=False)

class RandomHoming(Homing):

    def choose_target(self, target_group):
        choice = random.choice(target_group)
        return choice
