"""Implements a class for weapons.
"""

from astro.item import TimekeeperItem
from astro import FRIENDLY_SHIPS

class Weapon(TimekeeperItem):
    """A ship-mounted weapon.
    """
    required_fields = TimekeeperItem.required_fields + ('rate_of_fire', 'projectiles')
    defaults = {'FireBehavior': None, 'projectile_offsets': None}

    def __init__(self, key):
        TimekeeperItem.__init__(self, key)
        self.is_firing = False
        self.last_fired = 0.0

    def determine_projectile_offset(self, proj_i):
        if self.projectile_offsets:
            offset = self.projectile_offsets[proj_i]
            if isinstance(offset[0], list):
                # Cycling offset
                index = self.shot_indices[proj_i]
                offset_ = offset[index]
                self.shot_indices[proj_i] = (index + 1) % len(offset)
                offset = offset_
            offset = tuple(offset)
        else:
            offset = (0, 0)
        return offset

    def initialize(self):
        super().initialize()

        self.shot_interval = 1.0 / self.rate_of_fire

    def fire(self, now):
        """Fires the weapon.

        Creates a new instance of the weapon's projectile
        """

        if self.FireBehavior is not None:
            self.FireBehavior.FireWeapon(self)
        else:
            friendly = self.owner in FRIENDLY_SHIPS
            for i, projectile in enumerate(self.projectiles):
                projectile = projectile.copy()
                offset = self.determine_projectile_offset(i)
                projectile.place(self.owner.screen, firer=self.owner, friendly=friendly,
                    offset=offset)
        self.last_fired = now

    def is_ready_to_fire(self, now):
        return now - self.last_fired > self.shot_interval

    def place(self):
        self.shot_indices = [0] * len(self.projectiles)

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

    def damage_string(self):
        damages = list()

        for projectile in self.projectiles:
            damages.append(str(projectile.damage))

        return " + ".join(damages)
