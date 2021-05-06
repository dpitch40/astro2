import enum

import pygame

clock = pygame.time.Clock()
action_handlers = dict()

class Action(enum.Enum):
    QUIT = 0
    MAIN_MENU = 1
    GAME = 2

class NextAction:
    def __init__(self, action=Action.MAIN_MENU, params=None):
        self.action = action
        self.params = params

    def reset_next_action(self):
        self.action, self.params = None, None

    @property
    def selected(self):
        return self.action is not None

    def set_next_action(self, action, params=None):
        self.action = action
        self.params = params

def register_action(action, handler):
    action_handlers[action] = handler

def respond_to_action(screen):
    action = NEXT_ACTION.action
    NEXT_ACTION.reset_next_action()
    action_handlers[action](screen, NEXT_ACTION.params)

def gui_loop(screen):
    while NEXT_ACTION.action is not Action.QUIT:
        respond_to_action(screen)

NEXT_ACTION = NextAction()
