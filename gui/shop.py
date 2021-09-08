import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_selection_list import UISelectionList

from . import Action, MenuScreen
from .game import WeaponPreviewScreen
from astro import FONTS
from astro.player import active_player
from astro.weapon import Weapon
from astro.shield import Shield


class ShopScreen(MenuScreen):
    mapped_action = Action.SHOP
    title = "Shop"

    def __init__(self, screen, campaign):
        super().__init__(screen)
        self.campaign = campaign
        self.level = campaign.current_level()
        self.money_display = None
        self.item_display = None
        self.weapon_preview_rect = None
        self.weapon_preview = None
        self.selected_item = None
        self.selected_item_button = None
        self.owned_list = None
        self.owned_list_buttons = set()
        self.player = active_player()

    def draw_money_display(self):
        if self.money_display is not None:
            self.money_display.kill()
        self.money_display = UITextBox(f'Money: {self.player.money}§',
            relative_rect=self.proportional_rect((0.1, 0.25), (150, 25)),
            manager=self.manager, wrap_to_height=True)

    def item_selected(self, list_, item, button):
        if self.selected_item_button is not None:
            self.selected_item_button.unselect()
        if list_.get_single_selection() is not None:
            self.selected_item = item
            self.selected_item_button = button
        else:
            self.selected_item = self.selected_item_button = None

        self.draw_item_display()
        self.draw_weapon_preview()
        self.update_buttons()

    def draw_item_display(self):
        if self.item_display is not None:
            self.item_display.kill()
        if self.selected_item is not None:
            self.item_display = UITextBox(self.generate_item_string(),
                relative_rect=self.proportional_rect((0.1, 0.35), (250, 75)),
                manager=self.manager, wrap_to_height=True)

    def generate_item_string(self):
        item = self.selected_item
        name = f'Name: {item.name}'
        if self.player.equipped(item):
            name = f'{name} (equipped)'
        lines = [name, f'Cost: {item.cost}', f'Owned: {self.player.owned(item)}']

        if isinstance(item, Weapon):
            lines.append(f'Damage: {item.damage_string()}')
            lines.append(f'Rate Of Fire: {item.rate_of_fire}')

        if isinstance(item, Shield):
            lines.append(f'Capacity: {item.capacity}')
            lines.append(f'Recharge Rate: {item.recharge_rate}')
            lines.append(f'Recharge Delay: {item.recharge_delay}')

        return '<br/>'.join(lines)

    def draw_weapon_preview(self):
        if self.weapon_preview is not None:
            self.weapon_preview.teardown()

        if self.selected_item is not None:
            if isinstance(self.selected_item, Weapon):
                self.weapon_preview_rect = self.proportional_rect((0.1, 0.4), (350, 350))
                subscreen = pygame.Surface(self.weapon_preview_rect.size)
                subscreen.convert()
                self.weapon_preview = WeaponPreviewScreen(subscreen, self.selected_item)
                self.weapon_preview.setup()
            else:
                self.weapon_preview = None
                self.weapon_preview_rect = None

    def draw_owned_item_list(self):
        if self.owned_list is not None:
            # Reset
            self.owned_list.kill()
            for button in self.owned_list_buttons:
                del self.button_mapping[button]
            self.owned_list_buttons.clear()

        owned_items = self.player.owned_weapons + self.player.owned_shields
        # Goal: Instead of displaying a separate line for each item, display one line
        # for each item type plus a quantity amount if there are duplicates
        # e.g.:
        # TestGun1 (10000ξ)
        # TestGun2 x 10000 (1ξ)

        #Note how many of each item you own
        #Delete duplicate items from owned_items

        owned_item_strings = [f'{item.name} ({item.cost}ξ)' for item in owned_items]
        self.owned_list = UISelectionList(relative_rect=self.proportional_rect((0.5, 0.6), (0.35, 0.25)),
                                    item_list=owned_item_strings, manager=self.manager)

        for owned_item, list_item in zip(owned_items, self.owned_list.item_list):
            button = list_item["button_element"]
            self.button_mapping[button] = (self.item_selected, (self.owned_list, owned_item, button))
            self.owned_list_buttons.add(button)

    def setup(self):
        super().setup()
        buttons, self.button_mapping = self.button_list(
            [('Back', (Action.PRE_GAME, (self.campaign,))),
             ('Buy', (self.buy, ())),
             ('Sell', (self.sell, ())),
             ('Equip', (self.equip, ()))],
            (0.15, 0.8), (100, 25))

        self.draw_money_display()
        self.buy_button = buttons[1]
        self.sell_button = buttons[2]
        self.equip_button = buttons[3]
        self.update_buttons()

        shop_items = self.level.shop_items
        shop_item_strings = [f'{item.name} ({item.cost}ξ)' for item in shop_items]
        self.create_text('Shop', 24, bottomleft=(0.5, 0.25))
        shop_list = UISelectionList(relative_rect=self.proportional_rect((0.5, 0.25), (0.35, 0.25)),
                                    item_list=shop_item_strings, manager=self.manager)

        for shop_item, list_item in zip(shop_items, shop_list.item_list):
            button = list_item["button_element"]
            self.button_mapping[button] = (self.item_selected, (shop_list, shop_item, button))

        self.create_text('Owned', 24, bottomleft=(0.5, 0.6))
        self.draw_owned_item_list()

    def can_buy(self):
        return self.selected_item is not None and self.player.can_buy(self.selected_item)

    def buy(self):
        self.player.buy(self.selected_item)
        self.draw_money_display()
        self.draw_owned_item_list()
        self.update_buttons()
        self.draw_item_display()

    def can_sell(self):
        return self.selected_item is not None and self.player.can_sell(self.selected_item)

    def sell(self):
        self.player.sell(self.selected_item)
        self.draw_money_display()
        self.draw_owned_item_list()
        self.update_buttons()
        self.draw_item_display()

    def can_equip(self):
        return self.selected_item is not None and \
            self.player.owned(self.selected_item) and \
            not self.player.equipped(self.selected_item)

    def equip(self):
        self.player.equip(self.selected_item)
        self.update_buttons()
        self.draw_item_display()

    def update(self, elapsed=None):
        elapsed = super().update(elapsed)
        if self.weapon_preview is not None:
            self.weapon_preview.update(elapsed)
        return elapsed

    def update_display(self, elapsed):
        if self.weapon_preview is not None:
            self.weapon_preview.update_display(elapsed)
        super().update_display(elapsed)

    def update_buttons(self):
        if self.can_buy():
            self.buy_button.enable()
        else:
            self.buy_button.disable()

        if self.can_sell():
            self.sell_button.enable()
        else:
            self.sell_button.disable()

        if self.can_equip():
            self.equip_button.enable()
        else:
            self.equip_button.disable()

    def draw_non_ui(self):
        super().draw_non_ui()
        if self.weapon_preview_rect is not None:
            self.screen.blit(self.weapon_preview.screen, self.weapon_preview_rect)

    def teardown(self):
        if self.weapon_preview:
            self.weapon_preview.teardown()
