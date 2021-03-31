import pygame
import pygame.font

from astro import SCREEN_SIZE, HP_COLOR, SHIELD_COLOR, EMPTY_COLOR, BIG_HEALTHBAR_HEIGHT
from astro.healthbar import draw_healthbar_for_ship

class HUD:

    def __init__(self, screen, player_ship):
        self.screen = screen
        self.player_ship = player_ship
        self.hp_font = pygame.font.Font(None, 36)
        self.big_health_bar_rect = pygame.Rect(SCREEN_SIZE[0] // 4, 0, SCREEN_SIZE[0] // 2,
            BIG_HEALTHBAR_HEIGHT)
        self.big_health_bar_ship = None

    def draw(self):
        if self.player_ship.shield is not None:
            self.draw_shield_counter()
        self.draw_hp_counter()
        if self.big_health_bar_ship is not None:
            self.draw_big_health_bar()

    def draw_big_health_bar(self):
        draw_healthbar_for_ship(self.screen, self.big_health_bar_rect,
            self.big_health_bar_ship)

    def draw_shield_counter(self):
        s = f'{round(self.player_ship.shield.integrity, 1)}/{self.player_ship.shield.capacity}'
        text = self.hp_font.render(s, True, SHIELD_COLOR)
        textpos = text.get_rect(topright=(SCREEN_SIZE[0], 0))
        self.screen.blit(text, textpos)

    def draw_hp_counter(self):
        s = f'{self.player_ship.hp}/{self.player_ship.max_hp}'
        text = self.hp_font.render(s, True, HP_COLOR)
        textpos = text.get_rect(topright=(SCREEN_SIZE[0], text.get_height()))
        self.screen.blit(text, textpos)
