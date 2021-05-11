"""Implements a class for shields.
"""
import time

import pygame

from astro import FRIENDLY_SHIELDS, ENEMY_SHIELDS, FRIENDLY_SHIPS
from astro.astro_sprite import AstroSprite
from astro.item import TimekeeperItem
from astro.image import generate_rect_and_mask

class Shield(AstroSprite, TimekeeperItem):
    """A ship-mounted weapon.
    """
    required_fields = TimekeeperItem.required_fields + ('capacity', 'recharge_rate', 'recharge_delay')
    defaults = AstroSprite.defaults.copy()
    defaults.update({'color': (180, 180, 255),
                     'max_alpha': 128,
                     'imagepath': None,
                     'size_delta': 0,
                     'elasticity': 1.0})
    groups = []

    def __init__(self, key):
        AstroSprite.__init__(self, key)
        TimekeeperItem.__init__(self, key)
        self.is_recharging = False

    def collide_with_projectile(self, projectile):
        if self.integrity > 0:
            self.damage(projectile.damage)
            projectile.destroy()

    def collide_with_ship(self, other):
        if self.integrity > 0:
            return self.collide_with_mass(other)

    def collide_with_shield(self, other):
        if self.integrity > 0 and other.integrity > 0:
            return self.collide_with_mass(other)

    def damage(self, damage_amount):
        """Simulates the shield taking damage.

        Returns the amount of damage absorbed.
        """

        if damage_amount > 0:
            self.last_damaged = time.time()
            self.is_recharging = False

        self.integrity = max(0, self.integrity - damage_amount)

    def _load_image(self, *args, **kwargs):
        if self.imagepath is not None:
            return super()._load_image(*args, **kwargs)
        else:
            sizex, sizey = self.owner.rect.size
            sizex += self.size_delta
            sizey += self.size_delta
            image = pygame.Surface((sizex, sizey), flags=pygame.SRCALPHA)
            color = self.color + (self.max_alpha,)
            pygame.draw.ellipse(image, color, image.get_rect())
            return (image,) + generate_rect_and_mask(image)

    def initialize(self):
        # super().initialize()
        self.integrity = self.capacity
        self.last_damaged = time.time()

    def place(self, *args, **kwargs):
        self.groups = [FRIENDLY_SHIELDS] if FRIENDLY_SHIPS in self.owner.groups else \
            [ENEMY_SHIELDS]
        self.load_image()
        super().place(*args, **kwargs)

    @property
    def integrity_proportion(self):
        return self.integrity / self.capacity

    @property
    def mass(self):
        return self.owner.mass

    @property
    def x(self):
        return self.owner.x
    @x.setter
    def x(self, value):
        if hasattr(self, 'owner'):
            self.owner.x = value

    @property
    def y(self):
        return self.owner.y
    @y.setter
    def y(self, value):
        if hasattr(self, 'owner'):
            self.owner.y = value

    @property
    def speedx(self):
        return self.owner.speedx
    @speedx.setter
    def speedx(self, value):
        if hasattr(self, 'owner'):
            self.owner.speedx = value

    @property
    def speedy(self):
        return self.owner.speedy
    @speedy.setter
    def speedy(self, value):
        if hasattr(self, 'owner'):
            self.owner.speedy = value

    @property
    def kinetic_energy(self):
        return self.owner.kinetic_energy

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
        self.image.set_alpha(int(255 * self.integrity_proportion))
        self.update_position(elapsed)

    def sync_position(self):
        super().sync_position()
        self.owner.sync_position()

    def update_position(self, elapsed):
        # Keep shield centered on owner ship
        self.rect.center = self.owner.rect.center
