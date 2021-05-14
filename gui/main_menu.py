import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen
from astro.level import Level

class MainMenuScreen(MenuScreen):
    mapped_action = Action.MAIN_MENU
    title = "Homing Hose Simulator"

    def run(self):
        first_level = Level.instance('level1')
        first_level.screen = self

        buttons, button_mapping = self.button_list(
            [('Play Game', (Action.PRE_GAME, (first_level,))),
             ('Quit', (Action.QUIT, None))], (0.15, 300), (100, 25))

        self.button_loop(button_mapping)
