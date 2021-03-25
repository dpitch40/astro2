"""Defines a class for ships, and subclasses for player-controlled and hostile ships.
"""

import pygame

from astro import FRIENDLY_SHIPS, ENEMY_SHIPS
from astro.astro_sprite import AstroSprite

class Ship(AstroSprite):
    required_fields = ('imagepath', 'acceleration', 'max_speed', 'weapons', 'max_hp')
    confined = True

    def __init__(self, key):
        super().__init__(key)
        self.weapons = list()
        self.shield = None

    def initialize(self):
        super().initialize()

        for weapon in self.weapons:
            weapon.owner = self

        self.hp = self.max_hp

    def load_image(self):
        super().load_image()

        # Optionally, load the engine glow image
        if hasattr(self, 'engine_glow_imagepath'):
            self.static_image = self.image
            engine_glow = self._load_image(self.engine_glow_imagepath)
            self.moving_image = self.image.copy()
            self.moving_image.blit(engine_glow, (0, 0))
        else:
            self.moving_image, self.static_image = None, None

        if self.shield is not None:
            self.shield_image = pygame.Surface(self.rect.size)
            pygame.draw.ellipse(self.shield_image, (180, 180, 255, 128), self.shield_image.get_rect())

    def tick(self, now, elapsed):
        self.update_velocity(elapsed)

        super().tick(now, elapsed)

        if self.shield is not None:
            self.shield.tick(now, elapsed)

        for weapon in self.weapons:
            weapon.tick(now, elapsed)

        self.update_image()

    def update_image(self):
        # if self.shield is not None:
        #     pygame.draw.ellipse(self.image, (220, 220, 255, int(64 * self.shield.integrity_proportion)),
        #         self.image.get_rect())

        # self.image = self.image.conve
        pass

    def damage(self, damage_amount):
        if self.shield is not None:
            damage_absorbed = self.shield.damage(damage_amount)
            damage_amount -= damage_absorbed
        if damage_amount > 0:
            self.hp -= damage_amount
            if self.hp <= 0:
                self.destroy()

    def collide_with_projectile(self, projectile):
        self.damage(projectile.damage)
        projectile.destroy()

class PlayerShip(Ship):
    groups = [FRIENDLY_SHIPS]
    inverted = True

    def __init__(self, key):
        super().__init__(key)

        self.is_firing = False
        self.dirx = 0
        self.diry = 0

    def place(self, startx=0.5, starty=0.75, speedx=0, speedy=0):
        """Overrides AstroSprite.place with default starting location.
        """
        return super().place(startx, starty, speedx, speedy)

    def update_velocity(self, elapsed):
        """Updates the ship's velocity based on the currently inputted directions.
        """

        # Calculate the target velocity
        targetx = self.dirx * self.max_speed
        targety = self.diry * self.max_speed

        self.accelerate_toward(elapsed, targetx, targety)

    def update_moving_image(self):
        """Updates the ship's image based on whether it is moving.
        """
    def update_image(self):
        if (self.dirx or self.diry) and self.image is self.static_image:
            self.image = self.moving_image
        elif not self.dirx and not self.diry and self.image is self.moving_image:
            self.image = self.static_image

        super().update_image()

    # Methods linked to player input

    def start_firing(self):
        for weapon in self.weapons:
            weapon.start_firing()

    def stop_firing(self):
        for weapon in self.weapons:
            weapon.stop_firing()

    def accel_left(self):
        self.dirx = max(self.dirx - 1, -1)
        self.update_moving_image()

    def accel_right(self):
        self.dirx = min(self.dirx + 1, 1)
        self.update_moving_image()

    def accel_up(self):
        self.diry = max(self.diry - 1, -1)
        self.update_moving_image()

    def accel_down(self):
        self.diry = min(self.diry + 1, 1)
        self.update_moving_image()

class EnemyShip(Ship):
    required_fields = ('imagepath', 'acceleration', 'max_speed', 'weapons',
                       'move_behavior', 'fire_behavior')
    groups = [ENEMY_SHIPS]

    def initialize(self):
        super().initialize()

        self.move_behavior.init_ship(self)
        self.fire_behavior.init_ship(self)

    def tick(self, now, elapsed):
        super().tick(now, elapsed)
        self.fire_behavior.update(now, elapsed)

    def update_velocity(self, elapsed):
        self.move_behavior.update_velocity(elapsed)
