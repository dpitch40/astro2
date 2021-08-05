import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen


class PreGameScreen(MenuScreen):
    mapped_action = Action.PRE_GAME
    title = "Pre-Level"

    def __init__(self, screen, campaign):
        self.campaign = campaign
        self.level = campaign.current_level()
        self.title = self.level.name
        super().__init__(screen)

    def setup(self):
        super().setup()
        buttons, self.button_mapping = self.button_list(
            [('Play Level', (Action.GAME, None)),
             ('Shop', (Action.SHOP, (self.campaign,))),
             ('Back', (Action.CAMPAIGN_SELECT, None)),
             ('Main Menu', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))
