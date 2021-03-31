import pygame

from astro import HEALTHBARS, HP_COLOR, SHIELD_COLOR, EMPTY_COLOR, HEALTHBAR_HEIGHT
from astro.timekeeper import Timekeeper

def _draw_bar(surface, rect, fill_pct, fillcolor):
    pygame.draw.rect(surface, EMPTY_COLOR, rect)
    fill_rect = rect.copy()
    fill_rect.width = int(fill_pct * rect.width)
    pygame.draw.rect(surface, fillcolor, fill_rect)

def draw_healthbar(surface, rect, hp_pct, shield_pct=None):
    if shield_pct is None:
        _draw_bar(surface, rect, hp_pct, HP_COLOR)
    else:
        shield_rect = rect.copy()
        shield_rect.height = rect.height // 2
        _draw_bar(surface, shield_rect, shield_pct, SHIELD_COLOR)
        hp_pct = rect.copy()
        hp_pct.height = rect.height // 2
        hp_pct.top = shield_rect.bottom
        _draw_bar(surface, hp_rect, hp_pct, HP_COLOR)

def draw_healthbar_for_ship(surface, rect, ship):
    kwargs = {}
    if ship.shield is not None:
        kwargs['shield_pct'] = ship.shield.integrity_proportion
    return draw_healthbar(surface, rect, ship.integrity_proportion, **kwargs)

class Healthbar(Timekeeper, pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self)
        Timekeeper.__init__(self)
        self.owner = owner
        HEALTHBARS.add(self)
        self.image = pygame.Surface((self.owner.rect.width, HEALTHBAR_HEIGHT))
        self.rect = self.image.get_rect()
        self.static_rect  = self.image.get_rect()

    def destroy(self):
        self.kill()

    def tick(self, now, elapsed):
        # Keep in sync with owner
        self.rect.midtop = self.owner.rect.midbottom

        # Update image
        draw_healthbar_for_ship(self.image, self.static_rect, self.owner)
