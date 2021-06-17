import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen
from astro.level import Level
from astro.player import active_player

class MainMenuScreen(MenuScreen):
    mapped_action = Action.MAIN_MENU
    title = "Homing Hose Simulator"

    def setup(self):
        super().setup()
        current_level = active_player().level
        current_level.screen = self

        buttons, self.button_mapping = self.button_list(
            [('Play Game', (Action.PRE_GAME, (current_level,))),
             ('Quit', (Action.QUIT, None))], (0.15, 300), (100, 25))
