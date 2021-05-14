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

    def __init__(self, screen, level):
        super().__init__(screen)
        self.level = level

    def run(self):
        pygame.mouse.set_visible(False)

        background = pygame.Surface(self.screen.get_size()).convert()
        background.fill((0, 0, 0))

        font = pygame.font.Font(FONTS.mono_font, 48)
        deploying_msg = font.render("Deploying", 1, (255, 255, 255))
        deploying_pos = deploying_msg.get_rect(midbottom=(self.screen_size[0] / 2, self.screen_size[1] / 2))
        number_font = pygame.font.Font(FONTS.mono_font, 36)
        for number in (3, 2, 1):
            number_msg = number_font.render(f"{number}...", 1, (255, 255, 255))
            number_pos = number_msg.get_rect(midtop=(self.screen_size[0] / 2, self.screen_size[1] / 2 + 10))

            self.screen.blit(background, (0, 0))
            self.screen.blit(deploying_msg, deploying_pos)
            self.screen.blit(number_msg, number_pos)

            pygame.display.flip()

            self.clock.tick(1)

        player_ship = PlayerShip.instance('testship')
        hud = astro.HUD = HUD(self, player_ship)
        self.set_player_ship(player_ship)
        player_ship.place(self)
        self.level.start()

        while not NEXT_ACTION.selected:
            self.clock.tick(MAX_FPS)

            handle_ingame_events()

            check_collisions()

            for group in GROUPS:
                group.update()

            self.level.update()

            # Draw
            self.screen.blit(background, (0, 0))
            for group in GROUPS:
                group.draw(self.screen)

            hud.draw()
            pygame.display.flip()

    def set_player_ship(self, ship):
        astro.keys.PLAYER_SHIP = ship
