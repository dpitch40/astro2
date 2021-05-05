import os
import os.path
import sys
import enum
from functools import partial

import pygame
from pygame.locals import *
import thorpy

from astro import SCREEN_SIZE, GROUPS, MAX_FPS, CONFIG_DIR, CONFIG_ORDER, FONTS
import astro.keys
from astro.configurable import load_from_yaml
from astro.ship import PlayerShip
from astro.formation import Line
from astro.hud import HUD
from astro.level import Level
from astro.wave_condition import WaveCondition
from astro.collidable import check_collisions

# Imports to make sure all configurable classes have been initialized
import astro.weapon
import astro.shield
import astro.projectile
import astro.move_behavior
import astro.fire_behavior

clock = pygame.time.Clock()
screen = None
next_action = None

class Action(enum.Enum):
    QUIT = 0
    MAIN_MENU = 1
    GAME = 2

class NextAction:
    def __init__(self, action=Action.MAIN_MENU, params=None):
        self.action = action
        self.params = params

    def reset_next_action(self):
        self.action, self.params = None, None

    @property
    def selected(self):
        return self.action is not None

    def set_next_action(self, action, params=None):
        self.action = action
        self.params = params

def load_all():
    for d in CONFIG_ORDER:
        dirpath = os.path.join(CONFIG_DIR, d)
        for fname in os.listdir(dirpath):
            if os.path.splitext(fname)[1].lower() == '.yaml':
                load_from_yaml(os.path.join(dirpath, fname))

def set_player_ship(ship):
    astro.keys.PLAYER_SHIP = ship

def handle_ingame_events():
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            astro.keys.keydown(event.key, event.mod)
        elif event.type == KEYUP:
            astro.keys.keyup(event.key, event.mod)
        elif event.type == pygame.QUIT:
            sys.exit()

def init_game(player_ship):
    set_player_ship(player_ship)

# MAIN LOOPS

def run_main_menu():
    pygame.mouse.set_visible(True)

    font = pygame.font.Font(FONTS.mono_font, 60)
    title_msg = font.render("Homing Hose\nSimulator", 1, (255, 255, 255))
    title_pos = title_msg.get_rect(center=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 4))

    screen.fill((0, 0, 0))
    screen.blit(title_msg, title_pos)

    #declaration of some ThorPy elements ...
    button = thorpy.make_button("Play Game", func=partial(next_action.set_next_action, Action.GAME))
    quit_button = thorpy.make_button("Quit", func=partial(next_action.set_next_action, Action.QUIT))
    box = thorpy.Box(elements=[button, quit_button])
    #we regroup all elements on a menu, even if we do not launch the menu
    menu = thorpy.Menu(box)
    #important : set the screen as surface for all elements
    for element in menu.get_population():
        element.surface = screen
    
    box.set_center((SCREEN_SIZE[0] / 2,SCREEN_SIZE[1] / 2))
    box.blit()
    pygame.display.flip()

    while not next_action.selected:
        clock.tick(MAX_FPS / 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            menu.react(event) #the menu automatically integrate your elements

def run_game():
    pygame.mouse.set_visible(False)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill((0, 0, 0))

    font = pygame.font.Font(FONTS.mono_font, 48)
    deploying_msg = font.render("Deploying", 1, (255, 255, 255))
    deploying_pos = deploying_msg.get_rect(midbottom=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2))
    number_font = pygame.font.Font(FONTS.mono_font, 36)
    for number in (3, 2, 1):
        number_msg = font.render(f"{number}...", 1, (255, 255, 255))
        number_pos = number_msg.get_rect(midtop=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2 + 10))

        screen.blit(background, (0, 0))
        screen.blit(deploying_msg, deploying_pos)
        screen.blit(number_msg, number_pos)

        pygame.display.flip()

        clock.tick(1)

    load_all()
    player_ship = PlayerShip.instance('testship')
    hud = astro.HUD = HUD(screen, player_ship)
    init_game(player_ship)
    player_ship.place()
    level = Level.instance('level1')
    level.start()
    # enemy_ship.place(0.25, -300)
    # enemy_ship2.place(0.75, -300)

    while True:
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

def respond_to_action():
    action = next_action.action
    next_action.reset_next_action()
    if action is Action.GAME:
        run_game()
    elif action is Action.MAIN_MENU:
        run_main_menu()

def main():
    global screen
    global next_action

    pygame.init()
    FONTS.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Astro test')

    next_action = NextAction()

    while next_action.action is not Action.QUIT:
        respond_to_action()

    pygame.quit()

if __name__ == '__main__':
    main()
