import os.path
from logging import getLogger

import pygame

from astro.configurable import load_from_yaml

logger = getLogger('astro')

# TODO: Improve game config system--in-game options menu for many of these

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
SCREEN_SIZE = (640, 480)
OFF_SCREEN_CUTOFF = 500
MAX_FPS = 60

HP_COLOR = (60, 255, 60)
SHIELD_COLOR = (200, 200, 255)
EMPTY_COLOR = (255, 64, 64)

HUD = None
ENEMY_HEALTHBARS = True
BIG_HEALTHBAR_HEIGHT = 50
HEALTHBAR_HEIGHT = 10

BOUNCINESS_MULT = 5
COLLISION_DAMAGE_MULT = 1 / 50000

REACHED_DEST_THRESHOLD = 10

EXPLOSION_SIZE_SCALE = 1
EXPLOSION_DURATION_SCALE = 1

# Order in which to load configs
CONFIG_ORDER = ['behaviors',
                'projectiles',
                'shields',
                'weapons',
                'ships',
                'formations',
                'levels',]

def load_all():
    for d in CONFIG_ORDER:
        dirpath = os.path.join(CONFIG_DIR, d)
        for fname in os.listdir(dirpath):
            if os.path.splitext(fname)[1].lower() == '.yaml':
                load_from_yaml(os.path.join(dirpath, fname))

# Sprite groups

FRIENDLY_SHIPS = pygame.sprite.RenderPlain()
ENEMY_SHIPS = pygame.sprite.RenderPlain()
FRIENDLY_PROJECTILES = pygame.sprite.RenderPlain()
ENEMY_PROJECTILES = pygame.sprite.RenderPlain()
PICKUPS = pygame.sprite.RenderPlain()
OBJECTS = pygame.sprite.RenderPlain()
EXPLOSIONS = pygame.sprite.RenderPlain()
FRIENDLY_SHIELDS = pygame.sprite.RenderPlain()
ENEMY_SHIELDS = pygame.sprite.RenderPlain()
BACKGROUND_OBJECTS = pygame.sprite.RenderPlain()
HEALTHBARS = pygame.sprite.RenderPlain()

# All groups in update order
GROUPS = [
          BACKGROUND_OBJECTS,
          FRIENDLY_SHIPS,
          ENEMY_SHIPS,
          FRIENDLY_PROJECTILES,
          ENEMY_PROJECTILES,
          PICKUPS,
          OBJECTS,
          FRIENDLY_SHIELDS,
          ENEMY_SHIELDS,
          EXPLOSIONS,
          HEALTHBARS,
         ]

FRIENDLIES = {FRIENDLY_SHIPS, FRIENDLY_PROJECTILES}
ENEMIES = {ENEMY_SHIPS, ENEMY_PROJECTILES}

COLLIDABLE_PAIRS = [
                    (FRIENDLY_SHIELDS, ENEMY_SHIELDS, True),
                    (FRIENDLY_SHIELDS, ENEMY_SHIPS, True),
                    (FRIENDLY_SHIPS, ENEMY_SHIELDS, True),
                    (FRIENDLY_SHIPS, ENEMY_SHIPS, True),

                    (FRIENDLY_SHIELDS, ENEMY_PROJECTILES, True),
                    (ENEMY_SHIELDS, FRIENDLY_PROJECTILES, False),
                    (FRIENDLY_SHIPS, ENEMY_PROJECTILES, True),
                    (ENEMY_SHIPS, FRIENDLY_PROJECTILES, False),

                    (FRIENDLY_SHIPS, PICKUPS, False),
                    (FRIENDLY_SHIPS, OBJECTS, True),
                    (ENEMY_SHIPS, OBJECTS, False),
                    (FRIENDLY_PROJECTILES, OBJECTS, False),
                    (ENEMY_PROJECTILES, OBJECTS, False)]

# Fonts

class Fonts:
    mono_fontnames = ['dejavusansmono', 'ubuntumono', 'liberationmono', 'couriernew']

    def init(self):
        self.mono_font = pygame.font.match_font(self.mono_fontnames)

FONTS = Fonts()
