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
    PRE_GAME = 4

class ScreenMeta(type):
    def __init__(self, *args, **kwargs):
        type.__init__(self, *args, **kwargs)
        if self.mapped_action is not None:
            _screen_lookup[self.mapped_action] = self

class Screen(metaclass=ScreenMeta):
    clock = pygame.time.Clock()
    mapped_action = None

    def __init__(self, screen):
        self.screen = screen

    def run(self):
        raise NotImplementedError

class MenuScreen(Screen):
    title = None

    def __init__(self, screen):
        super().__init__(screen)
        self.manager = pygame_gui.UIManager(SCREEN_SIZE)
        pygame.mouse.set_visible(True)
        self.setup()

    def setup(self):
        font = pygame.font.Font(FONTS.mono_font, 48)
        self.title_msg = font.render(self.title, 1, (255, 255, 255))
        self.title_pos = self.title_msg.get_rect(midtop=(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 12))

    def draw_screen_and_title(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_msg, self.title_pos)

    def button_loop(self, button_mapping):
        while not NEXT_ACTION.selected:
            elapsed = self.loop_inner(button_mapping)
            self.update_display(elapsed)

    def loop_inner(self, button_mapping):
        elapsed = self.clock.tick(MAX_FPS / 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                NEXT_ACTION.set_next_action(Action.QUIT, None)
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element in button_mapping:
                        action, params = button_mapping[event.ui_element]
                        if callable(action):
                            action(*params)
                        else:
                            NEXT_ACTION.set_next_action(action, params)
            self.manager.process_events(event)

        return elapsed

    def update_display(self, elapsed):
        self.manager.update(elapsed / 1000)
        self.draw_screen_and_title()
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
    params = NEXT_ACTION.params
    NEXT_ACTION.reset_next_action()
    _screen_lookup[action](screen, *params).run()

def gui_loop(screen):
    while NEXT_ACTION.action is not Action.QUIT:
        respond_to_action(screen)

NEXT_ACTION = NextAction()
