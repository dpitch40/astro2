"""Implements a class for projectiles (friendly or hostile).
"""

import math
import random

import pygame

from astro.astro_sprite import AstroSprite
from astro.image import load_image
from astro import FRIENDLY_PROJECTILES, ENEMY_PROJECTILES
from astro.util import frange, angle_distance

class Projectile(AstroSprite):
    """A projectile fired by a weapon.
    """

    required_fields = ('imagepath', 'speed', 'damage')
    defaults = {"angle": 0, 'relative_to_firer_velocity': True, 'fuel_duration': None,
        "piercing": 1, 'angle_jitter': None, 'move_behavior': None, 'effects': None}

    FACING_DIRECTIONS = 8

    def initialize(self):
        super().initialize()
        self.colliding_with = None

        if self.effects is None:
            self.effects = list()

        if self.move_behavior is not None:
            self.move_behavior = self.move_behavior.copy()
            self.move_behavior.init_ship(self)

    def load_image(self):
        """Loads the image file for this object and initializes its image and rectangle
            attributes as expected by pygame.sprite.Sprite.
        """
        self.image, self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
            self.mask_rect_offsety, self.mask_centroid = \
            self._load_image(self.imagepath, directions=self.FACING_DIRECTIONS)


    def place(self, screen, firer, friendly, angle=None, offset=None):
        self.firer = firer
        # Also firing from hardpoint positions and not the center of the firer
        self.groups = [FRIENDLY_PROJECTILES] if friendly else [ENEMY_PROJECTILES]
        if angle is None:
            angle = self.angle + (180 if friendly else 0)
        if self.angle_jitter is not None:
            angle += random.uniform(-self.angle_jitter, self.angle_jitter)
        angle = math.radians(angle)
        speedx = math.sin(angle) * self.speed
        speedy = math.cos(angle) * self.speed
        if self.relative_to_firer_velocity:
            speedx += firer.speedx
            speedy += firer.speedy
        x = firer.rect.centerx
        y = firer.rect.centery
        if offset:
            x += offset[0]
            y += offset[1]
        super().place(screen, x, y, speedx=speedx, speedy=speedy)

    def collide_with_ship(self, ship):
        if self.alive() and self.colliding_with is not ship:
            ship.damage(self.damage)
            for effect in self.effects:
                effect.apply(ship)
            if self.piercing > 1 or self.piercing < 0:
                self.piercing -= 1
                self.colliding_with = ship
            else:
                self.destroy()

    def stop_colliding_with_ship(self, ship):
        self.colliding_with = None
        # If homing, reacquire target
        if self.move_behavior is not None and hasattr(self.move_behavior, 'acquire_target'):
            self.move_behavior.acquire_target()

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
        if self.move_behavior is not None and (self.fuel_duration is None or self.fuel_duration > 0):
            self.move_behavior.update_velocity(elapsed)
