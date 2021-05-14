import enum

import pygame
import pygame_gui
from pygame_gui.elements.ui_button import UIButton

import astro
from astro import MAX_FPS, FONTS

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
        self.screen_size = self.screen.get_size()
        self.top_level = self.screen is astro.SCREEN

    # Utility methods
    def convert_prop_x(self, x):
        if isinstance(x, int):
            return x
        else:
            return round(x * self.screen_size[0])

    def convert_prop_y(self, y):
        if isinstance(y, int):
            return y
        else:
            return round(y * self.screen_size[1])

    def convert_proportional_coordinates(self, x, y):
        return self.convert_prop_x(x), self.convert_prop_y(y)

    def convert_proportional_coordinate_list(self, coords):
        """Converts a list of (x, y)-tuples from floats between 0 and 1 (proportions of the screen size)
           to pixel coordinates.
        """

        return [self.convert_proportional_coordinates(x, y) for x, y in coords]

    def proportional_rect(self, pos, size):
        size = self.convert_proportional_coordinates(*size)
        pos = self.convert_proportional_coordinates(*pos)
        return pygame.Rect(pos, size)

    # Subclasses may want to override these

    def done(self):
        return NEXT_ACTION.selected

    def run(self):
        self.setup()
        while not self.done():
            elapsed = self.update()
            self.update_display(elapsed)

    def setup(self):
        pass

    def update(self, elapsed=None):
        if elapsed is None:
            elapsed = self.clock.tick(self.fps)
        return elapsed

    def update_display(self, elapsed):
        if self.top_level:
            pygame.display.flip()

class MenuScreen(Screen):
    title = None
    fps = MAX_FPS // 2

    def __init__(self, screen):
        super().__init__(screen)
        self.manager = pygame_gui.UIManager(self.screen_size)
        pygame.mouse.set_visible(True)
        self.button_mapping = dict()

    def setup(self):
        font = pygame.font.Font(FONTS.mono_font, 48)
        self.title_msg = font.render(self.title, 1, (255, 255, 255))
        self.title_pos = self.title_msg.get_rect(midtop=(self.screen_size[0] / 2, self.screen_size[1] / 12))

    def button_list(self, button_info,
                    pos, button_size, button_spacing=1.2, vertical=True):
        if vertical:
            spacing = self.convert_prop_y(button_size[1]) * button_spacing
        else:
            spacing = self.convert_prop_x(button_size[0]) * button_spacing

        x, y = self.convert_proportional_coordinates(*pos)
        buttons = list()
        button_mapping = dict()
        for text, (function, params) in button_info:
            button = UIButton(relative_rect=self.proportional_rect((round(x), round(y)), button_size),
                                   text=text, manager=self.manager)
            buttons.append(button)
            button_mapping[button] = (function, params)
            if vertical:
                y += spacing
            else:
                x += spacing

        return button, button_mapping

    def draw_screen_and_title(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_msg, self.title_pos)

    def update(self, elapsed=None):
        elapsed = super().update(elapsed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                NEXT_ACTION.set_next_action(Action.QUIT, None)
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element in self.button_mapping:
                        action, params = self.button_mapping[event.ui_element]
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
        super().update_display(elapsed)

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
