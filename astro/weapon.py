"""Implements a class for weapons.
"""

from astro.configurable import Configurable
from astro.timekeeper import Timekeeper

class Weapon(Configurable, Timekeeper):
    """A ship-mounted weapon.
    """
    required_fields = ('rate_of_fire', 'projectile')

    def __init__(self, key):
        Configurable.__init__(self, key)
        Timekeeper.__init__(self)
        self.is_firing = False
        self.last_fired = 0.0

    def initialize(self):
        super().initialize()

        self.shot_interval = 1.0 / self.rate_of_fire

    def fire(self, now):
        """Fires the weapon.

        Creates a new instance of the weapon's projectile
        """

        # TODO: Support multiple projectiles and firing directions other than forward
        projectile = self.projectile.copy()
        projectile.place(firer=self.owner, friendly=self.owner.inverted)
        self.last_fired = now

    def start_firing(self):
        """Tells the weapon to start firing.
        """
        self.is_firing = True

    def stop_firing(self):
        """Tells the weapon to stop firing.
        """
        self.is_firing = False

    def tick(self, now, elapsed):
        if self.is_firing:
            # Check if this weapon is ready to fire again
            if now - self.last_fired > self.shot_interval:
                self.fire(now)
