import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from pygame_gui.elements.ui_selection_list import UISelectionList
from pygame_gui.elements.ui_text_box import UITextBox

from . import Action, MenuScreen
from .game import WeaponPreviewScreen
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
        self.weapon_preview_rect = None
        self.weapon_preview = None
        self.selected_item = None
        self.selected_item_button = None
        self.player = active_player()

    def draw_money_display(self):
        if self.money_display is not None:
            self.money_display.kill()
        self.money_display = UITextBox(f'Money: {self.player.money}§',
            relative_rect=self.proportional_rect((0.1, 0.25), (150, 25)),
            manager=self.manager, wrap_to_height=True)

    def item_selected(self, item, button):
        self.selected_item = item
        self.selected_item_button = button
        self.draw_item_display(item)
        self.draw_weapon_preview(item)

    def draw_item_display(self, item):
        if self.item_display is not None:
            self.item_display.kill()
        self.item_display = UITextBox(self.generate_item_string(item),
            relative_rect=self.proportional_rect((0.1, 0.35), (250, 75)),
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

    def draw_weapon_preview(self, item):
        if self.weapon_preview is not None:
            self.weapon_preview.teardown()

        if isinstance(item, Weapon):
            self.weapon_preview_rect = self.proportional_rect((0.1, 0.4), (350, 350))
            subscreen = pygame.Surface(self.weapon_preview_rect.size)
            subscreen.convert()
            self.weapon_preview = WeaponPreviewScreen(subscreen, item)
            self.weapon_preview.setup()
        else:
            self.weapon_preview = None
            self.weapon_preview_rect = None

    def setup(self):
        super().setup()
        buttons, self.button_mapping = self.button_list(
            [('Back', (Action.PRE_GAME, (self.level,)))], (0.15, 0.8), (100, 25))

        shop_items = self.level.shop_items
        list_items = [f'{item.name} ({item.cost}ξ)' for item in shop_items]
        test_list = UISelectionList(relative_rect=self.proportional_rect((0.5, 0.3), (250, 250)),
                                    item_list=list_items, manager=self.manager)
        self.draw_money_display()

        for shop_item, list_item in zip(shop_items, test_list.item_list):
            button = list_item["button_element"]
            self.button_mapping[button] = (self.item_selected, (shop_item, button))

    def update(self, elapsed=None):
        elapsed = super().update(elapsed)
        if self.weapon_preview is not None:
            self.weapon_preview.update(elapsed)
        return elapsed

    def update_display(self, elapsed):
        if self.weapon_preview is not None:
            self.weapon_preview.update_display(elapsed)
        super().update_display(elapsed)

    def draw_non_ui(self):
        super().draw_non_ui()
        if self.weapon_preview_rect is not None:
            self.screen.blit(self.weapon_preview.screen, self.weapon_preview_rect)
