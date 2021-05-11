import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import Action, MenuScreen
from gui.util import button_list
from astro.util import proportional_rect


class ShopScreen(MenuScreen):
    mapped_action = Action.SHOP
    title = "Shop"

    def run(self):
        buttons, button_mapping = button_list(self.manager, 
            [('Back', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))

        items = ['Thing1 (1000)',
                 'Thing2 (2000)',
                 'Thing3 (3000)']
        test_list = UISelectionList(relative_rect=proportional_rect((0.5, 0.3), (250, 250)),
                                    item_list=items, manager=self.manager)

        self.button_loop(button_mapping)
