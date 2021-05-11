import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen
from gui.util import button_list


class MainMenuScreen(MenuScreen):
    mapped_action = Action.MAIN_MENU
    title = "Homing Hose Simulator"

    def run(self):
        buttons, button_mapping = button_list(self.manager, 
            [('Play Game', (Action.GAME, None)),
             ('Shop', (Action.SHOP, None)),
             ('Quit', (Action.QUIT, None))], (0.15, 300), (100, 25))

        self.button_loop(button_mapping)
