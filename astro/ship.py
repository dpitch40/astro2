"""Defines a class for ships, and subclasses for player-controlled and hostile ships.
"""

import math
import heapq

import pygame

import astro
from astro import FRIENDLY_SHIPS, ENEMY_SHIPS, ENEMY_HEALTHBARS
from astro.image import load_image
from astro.astro_sprite import AstroSprite
from astro.healthbar import Healthbar
from astro.explosion import Explosion
from astro.weapon import Weapon
from astro.shield import Shield

class Ship(AstroSprite):
    required_fields = ('imagepath', 'acceleration', 'max_speed', 'weapons', 'max_hp')
    defaults = AstroSprite.defaults.copy()
    defaults.update({'shield': None,
                     'mass': None,
                     'engine_glow_imagepath': None})
    confined = True

    def __init__(self, key):
        super().__init__(key)
        self.weapons = list()
        # List/heap of (end_time, effect) tuples
        self.timed_effects = list()

    def calculate_mass(self):
        return self.mask.count()

    def destroy(self):
        super().destroy()
        if self.shield is not None:
            self.shield.destroy()

        self.explode()

    def explode(self):
        explosion = Explosion(self)
        explosion.place(self.screen, self.rect.centerx, self.rect.centery, self.speedx, self.speedy)

    def initialize(self):
        super().initialize()

        for weapon in self.weapons:
            weapon.owner = self
        if self.shield is not None:
            self.shield.owner = self

        self.hp = self.max_hp

    @property
    def integrity_proportion(self):
        return self.hp / self.max_hp

    def load_image(self):
        super().load_image()

        # Optionally, load the engine glow image
        if self.engine_glow_imagepath is not None:
            self.static_image = self.image
            engine_glow = load_image(self.engine_glow_imagepath)[0]
            if self.inverted:
                engine_glow = pygame.transform.flip(engine_glow, False, True)
            self.moving_image = self.image.copy()
            self.moving_image.blit(engine_glow, (0, 0))
        else:
            self.moving_image, self.static_image = None, None

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        if self.shield is not None:
            self.shield.place(self.screen, self.rect.centerx, self.rect.centery)

        # Set mass (for collisions)
        if self.mass is None:
            self.mass = self.calculate_mass()

    def tick(self, now, elapsed):
        self.update_velocity(elapsed)

        super().tick(now, elapsed)

        # Check timed effects
        while self.timed_effects and self.timed_effects[0][0] < now:
            _, effect = heapq.heappop(self.timed_effects)
            effect.stop(self)

        for weapon in self.weapons:
            weapon.tick(now, elapsed)

        self.update_image()

    def update_image(self):
        pass

    def damage(self, damage_amount):
        self.hp -= damage_amount
        if self.hp <= 0:
            self.destroy()

    def collide_with_ship(self, other):
        return self.collide_with_mass(other)

class PlayerShip(Ship):
    groups = [FRIENDLY_SHIPS]
    inverted = True

    def __init__(self, key):
        super().__init__(key)

        self.is_firing = False
        self.dirx = 0
        self.diry = 0

    def equipped(self, item):
        if isinstance(item, Weapon):
            for w in self.weapons:
                if w.key == item.key:
                    return True
            return False
        else:
            return self.shield.key == item.key

    def equip(self, item):
        # TODO
        if isinstance(item, Weapon):
            self.weapons = [item]
        else:
            self.shield = item
        item.owner = self

    def place(self, screen, startx=0.5, starty=0.75, speedx=0, speedy=0):
        """Overrides AstroSprite.place with default starting location.
        """
        return super().place(screen, startx, starty, speedx, speedy)

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
    defaults = Ship.defaults.copy()
    defaults.update({'big_health_bar': False, 'enable_small_health_bar': True,
                     'overridden_move_behavior': None,
                     'overridden_move_behavior_duration': None,
                     'overridden_fire_behavior': None,
                     'overridden_fire_behavior_duration': None})
    groups = None
    confined = False

    def destroy(self):
        super().destroy()
        if self.big_health_bar:
            astro.HUD.big_health_bar_ship = None
        if ENEMY_HEALTHBARS and self.enable_small_health_bar:
            self.healthbar.destroy()

    def initialize(self):
        super().initialize()

        self.move_behavior = self.move_behavior.copy()
        self.fire_behavior = self.fire_behavior.copy()
        self.groups = [ENEMY_SHIPS]

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self.move_behavior.init_ship(self)
        self.fire_behavior.init_ship(self)
        if self.big_health_bar:
            astro.HUD.big_health_bar_ship = self
        if ENEMY_HEALTHBARS and self.enable_small_health_bar:
            self.healthbar = Healthbar(self)

    def become_friendly(self):
        self._switch_sides(ENEMY_SHIPS, FRIENDLY_SHIPS)

    def become_enemy(self):
        self._switch_sides(FRIENDLY_SHIPS, ENEMY_SHIPS)

    def _switch_sides(self, from_group, to_group):
        # For mind control
        self.groups.remove(from_group)
        self.groups.append(to_group)
        self.remove(from_group)
        self.add(to_group)

    def tick(self, now, elapsed):
        super().tick(now, elapsed)
        self.fire_behavior.update(now, elapsed)
