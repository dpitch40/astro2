import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements import UIButton
from  pygame_gui.elements.ui_selection_list import UISelectionList

from gui import NEXT_ACTION, clock, Action, register_action
from astro import SCREEN_SIZE, MAX_FPS, FONTS
from astro.util import proportional_rect


def run_main_menu(screen, _):
    pygame.mouse.set_visible(True)

    manager = pygame_gui.UIManager(SCREEN_SIZE)

    font = pygame.font.Font(FONTS.mono_font, 48)
    title_msg = font.render("Homing Hose Simulator", 1, (255, 255, 255))
    title_pos = title_msg.get_rect(center=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 4))

    screen.fill((0, 0, 0))
    screen.blit(title_msg, title_pos)

    play_button = UIButton(relative_rect=proportional_rect((0.15, 300), (100, 25)),
                           text='Play Game', manager=manager)

    quit_button = UIButton(relative_rect=proportional_rect((0.15, 350), (100, 25)),
                           text='Quit', manager=manager)

    test_list = UISelectionList(relative_rect=proportional_rect((0.5, 0.3), (250, 250)),
                                item_list=['Thing1', 'Thing2', 'Thing3'], manager=manager)

    while not NEXT_ACTION.selected:
        elapsed = clock.tick(MAX_FPS / 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                NEXT_ACTION.set_next_action(Action.QUIT, None)
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element is play_button:
                        NEXT_ACTION.set_next_action(Action.GAME, None)
                    elif event.ui_element is quit_button:
                        NEXT_ACTION.set_next_action(Action.QUIT, None)
            manager.process_events(event)

        manager.update(elapsed / 1000)
        manager.draw_ui(screen)
        pygame.display.update()

register_action(Action.MAIN_MENU, run_main_menu)
