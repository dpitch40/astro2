"""Implements a class for projectiles (friendly or hostile).
"""

import math

import pygame

from astro.astro_sprite import AstroSprite
from astro.image import load_image
from astro import FRIENDLY_PROJECTILES, ENEMY_PROJECTILES
from astro.timekeeper import Timekeeper
from astro.util import frange, angle_distance

class Projectile(AstroSprite, Timekeeper):
    """A projectile fired by a weapon.
    """

    required_fields = ('imagepath', 'speed', 'damage')
    defaults = {"angle": 0, 'relative_to_firer_velocity': True, 'fuel_duration': None}

    FACING_DIRECTIONS = 8

    def initialize(self):
        super().initialize()

        if hasattr(self, 'move_behavior'):
            self.move_behavior = self.move_behavior.copy()
            self.move_behavior.init_ship(self)

    def load_image(self):
        """Loads the image file for this object and initializes its image and rectangle
            attributes as expected by pygame.sprite.Sprite.
        """
        self.image, self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
            self.mask_rect_offsety, self.mask_centroid = \
            self._load_image(self.imagepath, directions=self.FACING_DIRECTIONS)


    def place(self, firer, friendly, angle=None):
        self.firer = firer
        # Also firing from hardpoint positions and not the center of the firer
        self.groups = [FRIENDLY_PROJECTILES] if friendly else [ENEMY_PROJECTILES]
        if angle is None:
            angle = self.angle + (180 if friendly else 0)
        angle = math.radians(angle)
        speedx = math.sin(angle) * self.speed
        speedy = math.cos(angle) * self.speed
        if self.relative_to_firer_velocity:
            speedx += firer.speedx
            speedy += firer.speedy
        super().place(firer.rect.centerx, firer.rect.centery, speedx=speedx, speedy=speedy)


    def tick(self, now, elapsed):
        if self.fuel_duration is not None:
            self.fuel_duration -= elapsed

        super().tick(now, elapsed)

        self.update_facing_direction()

    def update_facing_direction(self):
        direction = math.degrees(math.atan2(self.speedy, self.speedx))
        # Transform angle so 0 = facing down instead of right,
        # and positive angle increasesgo counterclockwise instead of clockwise
        direction = (90 - direction) % 360
        angles = [(-90 + a) % 360 for a in frange(0, 360, 360 / self.FACING_DIRECTIONS)]
        min_i, min_distance = 0, 360
        for i, angle in enumerate(angles):
            distance = angle_distance(direction, angle)
            if distance < min_distance:
                min_i, min_distance = i, distance
        angle = angles[min_i]
        key = self.imagepath + str(round(angle))

        image, rect, mask, mask_rect, mask_rect_offsetx, mask_rect_offsety, mask_centroid = \
            self._load_image(key)

        if image is not self.image:
            # Switch images
            center = self.rect.center
            self.image, self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
                self.mask_rect_offsety, self.mask_centroid = image, rect, mask, mask_rect, mask_rect_offsetx, \
                mask_rect_offsety, mask_centroid
            self.rect.center = center
            self.update_mask_pos()

    def update_velocity(self, elapsed):
        if hasattr(self, 'move_behavior') and self.fuel_duration > 0:
            self.move_behavior.update_velocity(elapsed)
