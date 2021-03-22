import pygame.font

from astro import SCREEN_SIZE

class HUD:

    def __init__(self, screen, player_ship):
        self.screen = screen
        self.player_ship = player_ship
        self.hp_font = pygame.font.Font(None, 36)
        self.hp_color = (255, 255, 255)

    def draw(self):
        self.draw_hp_counter()

    def draw_hp_counter(self):
        s = f'{self.player_ship.hp}/{self.player_ship.max_hp}'
        text = self.hp_font.render(s, True, self.hp_color)
        textpos = text.get_rect(topright=(SCREEN_SIZE[0], 0))
        self.screen.blit(text, textpos)
