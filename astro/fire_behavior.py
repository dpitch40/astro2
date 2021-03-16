from astro.configurable import Configurable

class FireBehavior(Configurable):
    def init_ship(self, ship):
        self.ship = ship
        self.weapons = ship.weapons

    def update(self, now, elapsed):
        pass

class FireConstantly(FireBehavior):
    """Causes the ship to fire as often as possible.
    """

    def update(self, now, elapsed):
        for weapon in self.weapons:
            if not weapon.is_firing:
                weapon.start_firing()
