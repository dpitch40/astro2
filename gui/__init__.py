import enum

import pygame
import pygame_gui

from astro import MAX_FPS, SCREEN_SIZE, FONTS
from gui.util import button_list

_screen_lookup = dict()

class Action(enum.Enum):
    QUIT = 0
    MAIN_MENU = 1
    GAME = 2
    SHOP = 3


class ScreenMeta(type):
    def __init__(self, *args, **kwargs):
        type.__init__(self, *args, **kwargs)
        if self.mapped_action is not None:
            _screen_lookup[self.mapped_action] = self

class Screen(metaclass=ScreenMeta):
    clock = pygame.time.Clock()
    screen = None
    mapped_action = None

    @classmethod
    def set_screen(cls, screen):
        cls.screen = screen

    def run(self):
        raise NotImplementedError

class MenuScreen(Screen):
    title = None

    def __init__(self, *params):
        self.manager = pygame_gui.UIManager(SCREEN_SIZE)
        pygame.mouse.set_visible(True)
        self.setup()

    def setup(self):
        font = pygame.font.Font(FONTS.mono_font, 48)
        title_msg = font.render(self.title, 1, (255, 255, 255))
        title_pos = title_msg.get_rect(midtop=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 12))

        self.screen.fill((0, 0, 0))
        self.screen.blit(title_msg, title_pos)

    def button_loop(self, button_mapping):
        while not NEXT_ACTION.selected:
            elapsed = self.clock.tick(MAX_FPS / 2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    NEXT_ACTION.set_next_action(Action.QUIT, None)
                elif event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        action, params = button_mapping[event.ui_element]
                        if callable(action):
                            action(*params)
                        else:
                            NEXT_ACTION.set_next_action(action, params)
                self.manager.process_events(event)

            self.manager.update(elapsed / 1000)
            self.manager.draw_ui(self.screen)
            pygame.display.update()

class NextAction:
    def __init__(self, action=Action.MAIN_MENU, params=None):
        self.set_next_action(action, params)

    def reset_next_action(self):
        self.action, self.params = None, list()

    @property
    def selected(self):
        return self.action is not None

    def set_next_action(self, action, params=None):
        self.action = action
        self.params = params if params is not None else list()


def respond_to_action(screen):
    action = NEXT_ACTION.action
    NEXT_ACTION.reset_next_action()
    _screen_lookup[action](*(NEXT_ACTION.params)).run()

def gui_loop(screen):
    while NEXT_ACTION.action is not Action.QUIT:
        respond_to_action(screen)

NEXT_ACTION = NextAction()
