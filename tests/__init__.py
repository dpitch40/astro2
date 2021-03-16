import uuid

import pygame

from astro import SCREEN_SIZE
from astro.astro_sprite import AstroSprite
from astro.ship import Ship
from astro.projectile import Projectile

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)

class AstroSpriteTest(AstroSprite):
    """Simplified version of AstroSprite with quick-creation methods and default image.
    """

    default_size = (1, 1)
    imagepath = ''

    def _load_image(self, rel_path):
        image = pygame.Surface(self.size)
        image.fill(pygame.Color(0, 0, 0))
        return image.convert()

    @classmethod
    def create(cls, size=None, startx=SCREEN_SIZE[0]/2, starty=SCREEN_SIZE[1]/2,
        speedx=0, speedy=0, key=None, config=None):
        return cls._create(size, key, config, startx=startx, starty=starty, speedx=speedx, speedy=speedy)

    @classmethod
    def _create(cls, size, key, config, **placekwargs):
        if size is None:
            size = cls.default_size
        if key is None:
            key = uuid.uuid4().hex
        if config is None:
            config = dict()

        inst = cls(key)
        inst._setup(config)
        inst.size = size
        inst.initialize()
        inst.place(**placekwargs)
        return inst

class ShipTest(AstroSpriteTest, Ship):
    default_size = (50, 50)
    engine_glow_imagepath = None

class ProjectileTest(AstroSpriteTest, Projectile):
    default_size = (10, 10)

    @classmethod
    def create(cls, firer=None, friendly=True, size=None, startx=SCREEN_SIZE[0]/2,
        starty=SCREEN_SIZE[1]/2, speedx=0, speedy=0, key=None, config=None):
        if firer is None:
            firer = ShipTest.create(startx=startx, starty=starty, speedx=speedx, speedy=speedy)

        return cls._create(size, key, config, firer=firer, friendly=friendly)
