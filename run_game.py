import pygame
from pygame.locals import *

import astro
from astro import SCREEN_SIZE, load_all, FONTS
from gui import gui_loop, Screen
from astro.player import Player

# Import UI modules
import gui.main_menu # pylint:disable=unused-import
import gui.game # pylint:disable=unused-import
import gui.shop # pylint:disable=unused-import
import gui.pre_game # pylint:disable=unused-import
import gui.campaign_select # pylint:disable=unused-import

# Imports to make sure all configurable classes have been initialized
import astro.ship
import astro.weapon # pylint:disable=unused-import
import astro.shield # pylint:disable=unused-import
import astro.projectile # pylint:disable=unused-import
import astro.move_behavior # pylint:disable=unused-import
import astro.fire_behavior # pylint:disable=unused-import
import astro.wave_condition # pylint:disable=unused-import
import astro.formation # pylint:disable=unused-import
import astro.level
import astro.effect
import astro.vfx
import astro.campaign


def main():
    pygame.init()
    FONTS.init()
    screen = astro.SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Astro test')
    load_all()
    gui_loop(screen)

    pygame.quit()

if __name__ == '__main__':
    main()
