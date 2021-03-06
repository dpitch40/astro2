"""Implements a class for weapons.
"""

from astro.item import TimekeeperItem

class Weapon(TimekeeperItem):
    """A ship-mounted weapon.
    """
    required_fields = ('rate_of_fire', 'projectiles')

    def __init__(self, key):
        TimekeeperItem.__init__(self, key)
        self.is_firing = False
        self.last_fired = 0.0

    def initialize(self):
        super().initialize()

        self.shot_interval = 1.0 / self.rate_of_fire

    def fire(self, now):
        """Fires the weapon.

        Creates a new instance of the weapon's projectile
        """

        if hasattr(self, "FireBehavior"):
            self.FireBehavior.FireWeapon(self)

        else:

            for projectile in self.projectiles:
                projectile = projectile.copy()
                projectile.place(firer=self.owner, friendly=self.owner.inverted)
        self.last_fired = now

    def is_ready_to_fire(self, now):
        return now - self.last_fired > self.shot_interval

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
            if self.is_ready_to_fire(now):
                self.fire(now)
