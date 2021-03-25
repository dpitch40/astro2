import os.path
from logging import getLogger

import pygame

logger = getLogger('astro')

# TODO: Improve game config system--in-game options menu for many of these

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
SCREEN_SIZE = (640, 480)
OFF_SCREEN_CUTOFF = 500
MAX_FPS = 60

# Order in which to load configs
CONFIG_ORDER = ['behaviors',
                'projectiles',
                'shields',
                'weapons',
                'ships']

# Sprite groups

FRIENDLY_SHIPS = pygame.sprite.RenderPlain()
ENEMY_SHIPS = pygame.sprite.RenderPlain()
FRIENDLY_PROJECTILES = pygame.sprite.RenderPlain()
ENEMY_PROJECTILES = pygame.sprite.RenderPlain()
PICKUPS = pygame.sprite.RenderPlain()
OBJECTS = pygame.sprite.RenderPlain()
BACKGROUND_OBJECTS = pygame.sprite.RenderPlain()

# All groups in update order
GROUPS = [
          BACKGROUND_OBJECTS,
          FRIENDLY_SHIPS,
          ENEMY_SHIPS,
          FRIENDLY_PROJECTILES,
          ENEMY_PROJECTILES,
          PICKUPS,
          OBJECTS,
         ]

FRIENDLIES = {FRIENDLY_SHIPS, FRIENDLY_PROJECTILES}
ENEMIES = {ENEMY_SHIPS, ENEMY_PROJECTILES}

COLLIDABLE_PAIRS = [(FRIENDLY_SHIPS, ENEMY_PROJECTILES),
                    (ENEMY_SHIPS, FRIENDLY_PROJECTILES),
                    (FRIENDLY_SHIPS, ENEMY_SHIPS),
                    (FRIENDLY_SHIPS, PICKUPS),
                    (FRIENDLY_SHIPS, OBJECTS),
                    (ENEMY_SHIPS, OBJECTS),
                    (FRIENDLY_PROJECTILES, OBJECTS),
                    (ENEMY_PROJECTILES, OBJECTS)]
