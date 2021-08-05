import os.path

import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements.ui_selection_list import UISelectionList

import astro
from . import NEXT_ACTION, Action, MenuScreen
from astro.campaign import Campaign
from astro.player import active_player

class CampaignSelectScreen(MenuScreen):
    mapped_action = Action.CAMPAIGN_SELECT
    title = "Choose a Campaign"

    def __init__(self, screen):
        super().__init__(screen)
        self.selected_campaign = None
        self.selected_campaign_button = None

    def campaign_selected(self, list_, campaign, button):
        if self.selected_campaign_button is not None:
            self.selected_campaign_button.unselect()
        if list_.get_single_selection() is not None:
            self.selected_campaign = campaign
            self.selected_campaign_button = button
        else:
            self.selected_campaign = self.selected_campaign_button = None

    def start_campaign(self):
        if self.selected_campaign is not None:
            NEXT_ACTION.set_next_action(Action.PRE_GAME, (self.selected_campaign,))
            active_player().campaign = self.selected_campaign
            self.selected_campaign.reset()

    def setup(self):
        super().setup()
        # current_level = active_player().level
        # current_level.screen = self

        campaign_strings = list()
        campaigns = sorted(Campaign.all_instances())
        for key, campaign in campaigns:
            num_levels = len(campaign.levels)
            levels_str = 'levels' if num_levels > 1 else 'level'
            campaign_strings.append(f'{campaign.name} ({num_levels} {levels_str})')
        # self.create_text('Shop', 24, bottomleft=(0.5, 0.25))
        campaign_list = UISelectionList(relative_rect=self.proportional_rect((0.5, 0.25), (0.35, 0.25)),
                                    item_list=campaign_strings, manager=self.manager)

        buttons, self.button_mapping = self.button_list(
            [('Play Campaign', (self.start_campaign, ())),
             ('Back', (Action.MAIN_MENU, None))], (0.15, 300), (100, 25))

        for (key, campaign), list_item in zip(campaigns, campaign_list.item_list):
            button = list_item["button_element"]
            self.button_mapping[button] = (self.campaign_selected, (campaign_list, campaign, button))
