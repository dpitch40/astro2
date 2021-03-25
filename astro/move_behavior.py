from astro.configurable import Configurable
from astro.util import magnitude, convert_proportional_coordinate_list
from astro import ENEMIES, FRIENDLY_SHIPS, ENEMY_SHIPS

class MoveBehavior(Configurable):
    defaults = {'reached_dest_threshold': 10,
                'initial_dest': None}

    def init_ship(self, ship):
        self.ship = ship

    def initialize(self):
        if self.initial_dest:
            self._pre_dest = self.initial_dest
        else:
            self._pre_dest = None

    def reached_dest(self, x, y):
        distance = magnitude(self.ship.x - x, self.ship.y - y)
        return distance < self.reached_dest_threshold

    def update_velocity(self, elapsed):
        """Updates the parent ship's velocity.
        """

        # Entry behavior
        if self._pre_dest:
            if not self.reached_dest(self._pre_dest):
                self.ship.accelerate_toward_point(elapsed, *self._pre_dest)
            else:
                self._pre_dest = None
        else:
            self._update_velocity(elapsed)

    def _update_velocity(self, elapsed):
        pass

class Patrol(MoveBehavior):
    """Causes the ship to move between a list of destinations in a loop.
    """

    required_fields = ('dests',)

    def initialize(self):
        super().initialize()
        self._dests = convert_proportional_coordinate_list(self.dests)
        self.dest_i = 0

    def _update_velocity(self, elapsed):
        dest = self._dests[self.dest_i]
        if self.reached_dest(*dest):
            # Cycle to next destination
            self.dest_i = (self.dest_i + 1) % len(self._dests)
            dest = self._dests[self.dest_i]

        self.ship.accelerate_toward_point(elapsed, *dest)

class Homing(MoveBehavior):
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
        # TODO: Improve this
        target = None
        try:
            target = next(iter(target_group))
        except StopIteration:
            pass
        return target

    def _update_velocity(self, elapsed):
        if self.target is None or not self.target.alive():
            self.target = self.acquire_target()
        
        if self.target is not None:
            self.ship.accelerate_toward_point(elapsed, self.target.x, self.target.y, decelerate=False)
