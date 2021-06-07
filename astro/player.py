"""Class for a player/game state.
"""
import yaml

import astro
from astro.configurable import load_from_obj
from astro.weapon import Weapon
from astro.shield import Shield
from astro.ship import Ship

class Player:
    def __init__(self):
        self.money = 10000#0
        self.owned_ships = list()
        self.owned_weapons = list()
        self.owned_shields = list()

    def get_item_list(self, item):
        if isinstance(item, Weapon):
            return self.owned_weapons
        elif isinstance(item, Shield):
            return self.owned_shields
        else:
            return self.owned_ships

    def owns(self, item):
        owned = self.get_item_list(item)
        key = item.key
        num_owned = 0
        for item_ in owned:
            if item_.key == key:
                num_owned += 1
        return num_owned

    def can_buy(self, item):
        return self.money >= item.cost and (isinstance(item, Weapon) or not self.owns(item))

    def buy(self, item):
        owned = self.get_item_list(item)
        self.money -= item.cost
        owned.append(item)

    def can_sell(self, item):
        return self.owns(item)

    def sell(self, item):
        owned = self.get_item_list(item)
        key = item.key
        del_i = None
        for i, item_ in enumerate(owned):
            if item_.key == key:
                del_i = i
                break
        del owned[del_i]
        self.money += item.cost

    def buy(self, item):
        owned = self.get_item_list(item)
        self.money -= item.cost
        owned.append(item)

    @classmethod
    def load(cls, filename):
        player = cls()
        with open(filename, 'r') as fobj:
            state = yaml.load(fobj)
        player.money = state['money']
        player.owned_ships = load_from_obj(state['owned_ships'])
        player.owned_weapons = load_from_obj(state['owned_weapons'])
        player.owned_shields = load_from_obj(state['owned_shields'])
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
