"""Implements a class for shields.
"""
import time

import pygame

from astro import SHIELDS
from astro.astro_sprite import AstroSprite
from astro.item import TimekeeperItem
from astro.image import generate_rect_and_mask

class Shield(AstroSprite, TimekeeperItem):
    """A ship-mounted weapon.
    """
    required_fields = ('capacity', 'recharge_rate', 'recharge_delay')
    defaults = {'color': (180, 180, 255),
                'max_alpha': 128,
                'imagepath': None}
    groups = [SHIELDS]

    def __init__(self, key):
        AstroSprite.__init__(self, key)
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

    def _load_image(self, *args, **kwargs):
        if self.imagepath is not None:
            return super()._load_image(*args, **kwargs)
        else:
            image = pygame.Surface(self.owner.rect.size)
            color = self.color + (self.max_alpha,)
            pygame.draw.ellipse(image, color, image.get_rect())
            return (image,) + generate_rect_and_mask(image)

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

        # Set alpha proportional to integrity
        self.image.set_alpha(int(128 * self.integrity_proportion))
