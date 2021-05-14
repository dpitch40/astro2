import time
import math

import pygame
from pygame.locals import KEYDOWN, KEYUP

from gui import NEXT_ACTION, Action, Screen
from astro import MAX_FPS, FONTS, GROUPS
import astro.keys
from astro.ship import PlayerShip
from astro.hud import HUD
from astro.level import Level
from astro.collidable import check_collisions

def handle_ingame_events():
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            astro.keys.keydown(event.key, event.mod)
        elif event.type == KEYUP:
            astro.keys.keyup(event.key, event.mod)
        elif event.type == pygame.QUIT:
            NEXT_ACTION.set_next_action(Action.QUIT, None)

class GameScreen(Screen):
    mapped_action = Action.GAME
    fps = MAX_FPS

    def __init__(self, screen, level):
        super().__init__(screen)

        self.level = level
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))

    def set_player_ship(self, ship):
        self.player_ship = ship
        astro.keys.PLAYER_SHIP = ship

    def setup(self):
        pygame.mouse.set_visible(False)

        self.set_player_ship(PlayerShip.instance('testship'))
        self.hud = astro.HUD = HUD(self, self.player_ship)
        self.player_ship.place(self)
        self.level.start()
        self.counting_down = True
        self.countdown_remaining = 3.0

        deploying_font = pygame.font.Font(FONTS.mono_font, 48)
        self.deploying_msg = deploying_font.render("Deploying", 1, (255, 255, 255))
        self.deploying_pos = self.deploying_msg.get_rect(midbottom=
            (self.screen_size[0] / 2, self.screen_size[1] / 2))

        self.number_font = pygame.font.Font(FONTS.mono_font, 36)

    def update_display(self, elapsed):
        self.screen.blit(self.background, (0, 0))
        if self.counting_down:
            self.screen.blit(self.deploying_msg, self.deploying_pos)
            countdown_num = str(int(math.ceil(self.countdown_remaining)))
            number_msg = self.number_font.render(f"{countdown_num}...", 1, (255, 255, 255))
            number_pos = number_msg.get_rect(midtop=(self.screen_size[0] / 2, self.screen_size[1] / 2 + 10))
            self.screen.blit(number_msg, number_pos)
        else:
            for group in GROUPS:
                group.draw(self.screen)

            if hasattr(self, 'hud'):
                self.hud.draw()
        super().update_display(elapsed)

    def update(self, elapsed=None):
        elapsed = super().update(elapsed)

        if self.counting_down:
            self.countdown_remaining -= elapsed / 1000
            if self.countdown_remaining <= 0:
                self.counting_down = False

        if not self.counting_down:
            self.clock.tick(MAX_FPS)

            handle_ingame_events()

            check_collisions()

            for group in GROUPS:
                group.update()

            self.level.update()

        return elapsed