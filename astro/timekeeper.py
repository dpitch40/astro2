"""Defines a superclass for objects that are updated each frame to keep track of the time
   since their last update.
"""

import time

class Timekeeper:
    def __init__(self):
        self._last_updated = None

    def _tick(self):
        now = time.time()
        if self._last_updated is not None:
            elapsed = now - self._last_updated
            self.tick(now, elapsed)
        self._last_updated = now

    def tick(self, now, elapsed):
        """Overridable method to be called once each "tick" of the game simulation.

        Args:
            now (float): The current timestamp
            elapsed (float): The time in fractional seconds since the object was last updated.
        """
        raise NotImplementedError

    def update(self):
        """Called by pygame.sprite.Group.update.
        """
        self._tick()
