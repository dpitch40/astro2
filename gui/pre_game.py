import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen


class PreGameScreen(MenuScreen):
    mapped_action = Action.PRE_GAME
    title = "Pre-Level"

    def __init__(self, screen, level):
        self.level = level
        self.title = self.level.name
        super().__init__(screen)

    def run(self):
        buttons, button_mapping = self.button_list(
            [('Play Level', (Action.GAME, (self.level,))),
             ('Shop', (Action.SHOP, (self.level,))),
             ('Main Menu', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))

        self.button_loop(button_mapping)
