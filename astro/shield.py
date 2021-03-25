"""Implements a class for shields.
"""
import time

from astro.item import TimekeeperItem

class Shield(TimekeeperItem):
    """A ship-mounted weapon.
    """
    required_fields = ('capacity', 'recharge_rate', 'recharge_delay')


    def __init__(self, key):
        TimekeeperItem.__init__(self, key)
        self.is_recharging = False

    def damage(self, damage_amount):
        """Simulates the shield taking damage.

        Returns the amount of damage absorbed.
        """

        if damage_amount > 0:
            self.last_damaged = time.time()

        if damage_amount <= self.integrity:
            self.integrity -= damage_amount
            return damage_amount
        else:
            absorbed = self.integrity
            self.integrity = 0
            return absorbed

    def initialize(self):
        super().initialize()
        self.integrity = self.capacity
        self.last_damaged = time.time()

    @property
    def integrity_proportion(self):
        return self.integrity / self.capacity

    def tick(self, now, elapsed):
        if not self.is_recharging and self.integrity < self.capacity and \
            now - self.last_damaged > self.recharge_delay:
            self.is_recharging = True

        if self.is_recharging:
            self.integrity = min(self.integrity + self.recharge_rate * elapsed,
                                 self.capacity)
            if self.integrity == self.capacity:
                self.is_recharging = False
