import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen
from gui.util import button_list


class PreGameScreen(MenuScreen):
    mapped_action = Action.PRE_GAME
    title = "Pre-Level"

    def __init__(self, level):
        self.level = level
        self.title = self.level.name
        super().__init__()

    def run(self):
        buttons, button_mapping = button_list(self.manager, 
            [('Play Level', (Action.GAME, (self.level,))),
             ('Shop', (Action.SHOP, (self.level,))),
             ('Main Menu', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))

        self.button_loop(button_mapping)