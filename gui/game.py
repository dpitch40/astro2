import pygame
from pygame.locals import KEYDOWN, KEYUP

from gui import NEXT_ACTION, clock, Action, register_action
from astro import SCREEN_SIZE, MAX_FPS, FONTS, GROUPS
import astro.keys
from astro.ship import PlayerShip
from astro.hud import HUD
from astro.level import Level
from astro.collidable import check_collisions

def set_player_ship(ship):
    astro.keys.PLAYER_SHIP = ship

def handle_ingame_events():
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            astro.keys.keydown(event.key, event.mod)
        elif event.type == KEYUP:
            astro.keys.keyup(event.key, event.mod)
        elif event.type == pygame.QUIT:
            NEXT_ACTION.set_next_action(Action.QUIT, None)

def init_game(player_ship):
    set_player_ship(player_ship)

def run_game(screen, _):
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill((0, 0, 0))

    font = pygame.font.Font(FONTS.mono_font, 48)
    deploying_msg = font.render("Deploying", 1, (255, 255, 255))
    deploying_pos = deploying_msg.get_rect(midbottom=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2))
    number_font = pygame.font.Font(FONTS.mono_font, 36)
    for number in (3, 2, 1):
        number_msg = number_font.render(f"{number}...", 1, (255, 255, 255))
        number_pos = number_msg.get_rect(midtop=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2 + 10))

        screen.blit(background, (0, 0))
        screen.blit(deploying_msg, deploying_pos)
        screen.blit(number_msg, number_pos)

        pygame.display.flip()

        clock.tick(1)

    player_ship = PlayerShip.instance('testship')
    hud = astro.HUD = HUD(screen, player_ship)
    init_game(player_ship)
    player_ship.place()
    level = Level.instance('level1')
    level.start()
    # enemy_ship.place(0.25, -300)
    # enemy_ship2.place(0.75, -300)

    while not NEXT_ACTION.selected:
        clock.tick(MAX_FPS)

        handle_ingame_events()

        check_collisions()

        for group in GROUPS:
            group.update()

        level.update()

        # Draw
        screen.blit(background, (0, 0))
        for group in GROUPS:
            group.draw(screen)

        hud.draw()
        pygame.display.flip()

register_action(Action.GAME, run_game)
