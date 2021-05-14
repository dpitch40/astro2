import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList
from pygame_gui.elements.ui_text_box import UITextBox

from gui import Action, MenuScreen
from gui.util import button_list
from astro.util import proportional_rect
from astro.player import active_player
from astro.weapon import Weapon
from astro.shield import Shield

class ShopScreen(MenuScreen):
    mapped_action = Action.SHOP
    title = "Shop"

    def __init__(self, screen, level):
        super().__init__(screen)
        self.level = level
        self.money_display = None
        self.item_display = None
        self.player = active_player()

    def draw_money_display(self):
        if self.money_display is not None:
            self.money_display.kill()
        self.money_display = UITextBox(f'Money: {self.player.money}§',
            relative_rect=proportional_rect((0.1, 0.25), (150, 25)),
            manager=self.manager, wrap_to_height=True)

    def item_selected(self, item):
        self.draw_item_display(item)

    def draw_item_display(self, item):
        if self.item_display is not None:
            self.item_display.kill()
        self.item_display = UITextBox(self.generate_item_string(item),
            relative_rect=proportional_rect((0.1, 0.35), (250, 75)),
            manager=self.manager, wrap_to_height=True)

    def generate_item_string(self, item):
        lines = [f'Name: {item.name}',  f'Cost: {item.cost}']

        if isinstance(item, Weapon):
            lines.append(f'Damage: {item.damage_string()}')
            lines.append(f'Rate Of Fire: {item.rate_of_fire}')

        if isinstance(item, Shield):
            lines.append(f'Capacity: {item.capacity}')
            lines.append(f'Recharge Rate: {item.recharge_rate}')
            lines.append(f'Recharge Delay: {item.recharge_delay}')

        return '<br/>'.join(lines)


    def run(self):
        buttons, button_mapping = button_list(self.manager, 
            [('Back', (Action.PRE_GAME, (self.level,)))], (0.15, 0.8), (100, 25))

        shop_items = self.level.shop_items
        list_items = [f'{item.name} ({item.cost}ξ)' for item in shop_items]
        test_list = UISelectionList(relative_rect=proportional_rect((0.5, 0.3), (250, 250)),
                                    item_list=list_items, manager=self.manager)
        self.draw_money_display()

        for shop_item, list_item in zip(shop_items, test_list.item_list):
            button = list_item["button_element"]
            button_mapping[button] = (self.item_selected, (shop_item,))

        self.button_loop(button_mapping)
