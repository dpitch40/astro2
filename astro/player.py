"""Class for a player/game state.
"""
import yaml

import astro

class Player:
    def __init__(self):
        self.money = 10000#0
        self.owned_ships = list()
        self.owned_weapons = list()
        self.owned_shields = list()

    @classmethod
    def load(cls, filename):
        player = cls()
        with open(filename, 'r') as fobj:
            state = yaml.load(fobj)
        player.money = state['money']
        player.owned_ships = state['owned_ships']
        player.owned_weapons = state['owned_weapons']
        player.owned_shields = state['owned_shields']
        return player

    def save(self, filename):
        state = {'money': self.money,
                 'owned_ships': [s.serialize() for s in self.owned_ships],
                 'owned_weapons': [s.serialize() for s in self.owned_weapons],
                 'owned_shields': [s.serialize() for s in self.owned_shields]}
        with open(filename, 'w') as fobj:
            yaml.dump(state, fobj)

def active_player():
    return astro.PLAYER

def load_player(filename):
    astro.PLAYER = Player.load(filename)

def save_player(filename):
    astro.PLAYER.save(filename)
