"""Module for handling keyboard input from the player.
"""

import pygame
from pygame.locals import *

PLAYER_SHIP = None

# TODO: Make this user-configurable

DOWN_ACTIONS = {
                K_LEFT: lambda: PLAYER_SHIP.accel_left(),
                K_RIGHT: lambda: PLAYER_SHIP.accel_right(),
                K_UP: lambda: PLAYER_SHIP.accel_up(),
                K_DOWN: lambda: PLAYER_SHIP.accel_down(),
                K_SPACE: lambda: PLAYER_SHIP.start_firing()
               }

UP_ACTIONS = {
                K_LEFT: lambda: PLAYER_SHIP.accel_right(),
                K_RIGHT: lambda: PLAYER_SHIP.accel_left(),
                K_UP: lambda: PLAYER_SHIP.accel_down(),
                K_DOWN: lambda: PLAYER_SHIP.accel_up(),
                K_SPACE: lambda: PLAYER_SHIP.stop_firing()
               }

def keydown(key, mod):
    """Callback for when a key is pressed.
    """
    if key in DOWN_ACTIONS:
        DOWN_ACTIONS[key]()

def keyup(key, mod):
    """Callback for when a key is released.
    """
    if key in UP_ACTIONS:
        UP_ACTIONS[key]()

def main():
    import sys
    pygame.init()

    size = width, height = 320, 240
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keydown(event.key, event.mod)
            elif event.type == KEYUP:
                keyup(event.key, event.mod)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(black)
        pygame.display.flip()

if __name__ == '__main__':
    main()
