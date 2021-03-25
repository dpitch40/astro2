import pygame.font

from astro import SCREEN_SIZE

class HUD:

    def __init__(self, screen, player_ship):
        self.screen = screen
        self.player_ship = player_ship
        self.hp_font = pygame.font.Font(None, 36)
        self.hp_color = (255, 255, 255)
        self.shield_color = (220, 220, 255)

    def draw(self):
        if self.player_ship.shield is not None:
            self.draw_shield_counter()
        self.draw_hp_counter()

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
