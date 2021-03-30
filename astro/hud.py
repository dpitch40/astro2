import pygame
import pygame.font

from astro import SCREEN_SIZE

class HUD:

    def __init__(self, screen, player_ship):
        self.screen = screen
        self.player_ship = player_ship
        self.hp_font = pygame.font.Font(None, 36)
        self.hp_color = (60, 255, 60)
        self.shield_color = (200, 200, 255)
        self.empty_color = (255, 64, 64)
        self.big_health_bar_ship = None

    def draw(self):
        if self.player_ship.shield is not None:
            self.draw_shield_counter()
        self.draw_hp_counter()
        if self.big_health_bar_ship is not None:
            self.draw_big_health_bar()

    def draw_big_health_bar(self):
        screen_width = SCREEN_SIZE[0]
        x_max = (screen_width * 3) // 4
        x_min = screen_width // 4
        y_min = 0
        y_max = 50
        if self.big_health_bar_ship.shield is not None:
            shield_bar_top, shield_bar_bottom = 0, y_max // 2
            health_bar_top, health_bar_bottom = y_max // 2, y_max
            self._draw_bar(x_min, x_max, shield_bar_top, shield_bar_bottom,
                self.big_health_bar_ship.shield.integrity_proportion,
                self.shield_color, self.empty_color)
        else:
            health_bar_top, health_bar_bottom = 0, y_max
        self._draw_bar(x_min, x_max, health_bar_top, health_bar_bottom,
            self.big_health_bar_ship.integrity_proportion,
            self.hp_color, self.empty_color)

    def _draw_bar(self, x_min, x_max, y_min, y_max, fill_pct, fillcolor, emptycolor):
        rect = pygame.Rect(x_min, y_min, (x_max - x_min), (y_max - y_min))
        pygame.draw.rect(self.screen, emptycolor, rect)
        x_max = x_min + int(fill_pct * (x_max - x_min))
        rect = pygame.Rect(x_min, y_min, (x_max - x_min), (y_max - y_min))
        pygame.draw.rect(self.screen, fillcolor, rect)

    def draw_shield_counter(self):
        s = f'{round(self.player_ship.shield.integrity, 1)}/{self.player_ship.shield.capacity}'
        text = self.hp_font.render(s, True, self.shield_color)
        textpos = text.get_rect(topright=(SCREEN_SIZE[0], 0))
        self.screen.blit(text, textpos)

    def draw_hp_counter(self):
        s = f'{self.player_ship.hp}/{self.player_ship.max_hp}'
        text = self.hp_font.render(s, True, self.hp_color)
        textpos = text.get_rect(topright=(SCREEN_SIZE[0], text.get_height()))
        self.screen.blit(text, textpos)
