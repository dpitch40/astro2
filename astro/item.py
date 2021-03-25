"""Implements a class for equippable items.
"""

from astro.configurable import Configurable
from astro.timekeeper import Timekeeper

class Item(Configurable):
    pass

class TimekeeperItem(Item, Timekeeper):
    def __init__(self, key):
        Item.__init__(self, key)
        Timekeeper.__init__(self)
