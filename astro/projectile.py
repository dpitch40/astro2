"""Implements a class for projectiles (friendly or hostile).
"""

import math

import pygame

from astro.astro_sprite import AstroSprite
from astro import FRIENDLY_PROJECTILES, ENEMY_PROJECTILES
from astro.timekeeper import Timekeeper

class Projectile(AstroSprite, Timekeeper):
    """A projectile fired by a weapon.
    """

    required_fields = ('imagepath', 'speed', 'damage')
    defaults = {"angle": 0}

    def initialize(self):
        super().initialize()

        if hasattr(self, 'move_behavior'):
            self.move_behavior = self.move_behavior.copy()
            self.move_behavior.init_ship(self)

    def load_image(self):
        """Loads the image file for this object and initializes its image and rectangle
            attributes as expected by pygame.sprite.Sprite.
        """
        # TODO: Cache images in memory to avoid reloading them every time
        self.down_image = self._load_image(self.imagepath)
        self.right_image = pygame.transform.rotate(self.down_image, 90)
        self.up_image = pygame.transform.rotate(self.down_image, 180)
        self.left_image = pygame.transform.rotate(self.down_image, 270)

        self.down_rect, self.down_mask, self.down_mask_rect = \
            self.generate_rect_and_mask(self.down_image)
        self.right_rect, self.right_mask, self.right_mask_rect = \
            self.generate_rect_and_mask(self.right_image)
        self.up_rect, self.up_mask, self.up_mask_rect = \
            self.generate_rect_and_mask(self.up_image)
        self.left_rect, self.left_mask, self.left_mask_rect = \
            self.generate_rect_and_mask(self.left_image)

        self.image = self.down_image
        self.rect = self.down_rect
        self.mask = self.down_mask
        self.mask_rect = self.down_mask_rect


    def place(self, firer, friendly):
        self.firer = firer
        # TODO: Base inversion on direction rather than friendly status
        # Also support facing right/left
        # Also firing from hardpoint positions and not the center of the firer
        self.inverted = friendly
        self.groups = [FRIENDLY_PROJECTILES] if friendly else [ENEMY_PROJECTILES]
        super().place(firer.rect.centerx, firer.rect.centery,
                      speedx=math.sin(math.radians(self.angle)) * self.speed + firer.speedx,
                      speedy=math.cos(math.radians(self.angle)) * self.speed * (-1 if friendly else 1) + firer.speedy)


    def tick(self, now, elapsed):
        super().tick(now, elapsed)

        direction = math.atan2(self.speedy, self.speedx)
        if math.pi / 4 < direction < 3 * math.pi / 4:
            # Up
            if self.image is not self.up_image:
                self.image = self.up_image
                self.up_rect.center = self.rect.center
                self.rect = self.up_rect
                self.mask = self.up_mask
                self.up_mask_rect.center = self.mask_rect.center
                self.mask_rect = self.up_mask_rect
        elif -math.pi / 4 < direction < math.pi / 4:
            # Right
            if self.image is not self.right_image:
                self.image = self.right_image
                self.right_rect.center = self.rect.center
                self.rect = self.right_rect
                self.mask = self.right_mask
                self.right_mask_rect.center = self.mask_rect.center
                self.mask_rect = self.right_mask_rect
                self.mask_rect = self.up_mask_rect
        elif -3 * math.pi / 4 < direction < -math.pi / 4:
            # Down
            if self.image is not self.down_image:
                self.image = self.down_image
                self.down_rect.center = self.rect.center
                self.rect = self.down_rect
                self.mask = self.down_mask
                self.down_mask_rect.center = self.mask_rect.center
                self.mask_rect = self.down_mask_rect
        else:
            # Down
            if self.image is not self.left_image:
                self.image = self.left_image
                self.left_rect.center = self.rect.center
                self.rect = self.left_rect
                self.mask = self.left_mask
                self.left_mask_rect.center = self.mask_rect.center
                self.mask_rect = self.left_mask_rect

    def update_velocity(self, elapsed):
        if hasattr(self, 'move_behavior'):
            self.move_behavior.update_velocity(elapsed)
