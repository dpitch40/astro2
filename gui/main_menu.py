import pygame
from pygame.locals import *
import pygame_gui

from gui import Action, MenuScreen
from astro.player import active_player

class MainMenuScreen(MenuScreen):
    mapped_action = Action.MAIN_MENU
    title = "Homing Hose Simulator"

    def setup(self):
        super().setup()

        buttons, self.button_mapping = self.button_list(
            [('Play Game', (Action.CAMPAIGN_SELECT, ())),
             ('Quit', (Action.QUIT, None))], (0.15, 300), (100, 25))
