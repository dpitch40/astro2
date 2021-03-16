from astro.configurable import Configurable
from astro.util import magnitude, convert_proportional_coordinate_list

class MoveBehavior(Configurable):
    def update_velocity(self, elapsed):
        """Updates the parent ship's velocity.
        """
        pass

class Patrol(MoveBehavior):
    """Causes the ship to move between a list of destinations in a loop.
    """
    defaults = {'reached_dest_threshold': 10}

    required_fields = ('dests',)

    def initialize(self):
        self._dests = convert_proportional_coordinate_list(self.dests)
        self.dest_i = 0

    def reached_dest(self, x, y):
        distance = magnitude(self.ship.x - x, self.ship.y - y)
        return distance < self.reached_dest_threshold

    def update_velocity(self, elapsed):
        dest = self._dests[self.dest_i]
        if self.reached_dest(*dest):
            # Cycle to next destination
            self.dest_i = (self.dest_i + 1) % len(self._dests)
            dest = self._dests[self.dest_i]

        self.ship.accelerate_toward_point(elapsed, *dest)
