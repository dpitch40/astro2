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

    def __init__(self, level):
        super().__init__()
        self.level = level

    def item_selected(self, item):
        pass

    def run(self):
        buttons, button_mapping = button_list(self.manager, 
            [('Back', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))

        shop_items = self.level.shop_items
        list_items = [f'{item.name} ({item.cost}ξ)' for item in shop_items]
        test_list = UISelectionList(relative_rect=proportional_rect((0.5, 0.3), (250, 250)),
                                    item_list=list_items, manager=self.manager)

        for shop_item, list_item in zip(shop_items, test_list.item_list):
            button = list_item["button_element"]
            button_mapping[button] = (self.item_selected, (shop_item,))

        self.button_loop(button_mapping)
