import math

import astro.keys
from astro.configurable import Configurable
from astro.util import magnitude, lead_target

class FireBehavior(Configurable):
    def init_ship(self, ship):
        self.ship = ship
        self.weapons = ship.weapons
        for weapon in self.weapons:
            weapon.FireBehavior = self

    def update(self, now, elapsed):
        pass

    def FireWeapon(self, Weapon):
        """Fires the weapon, if the weapon has a fire behavior that does not modify the firing
        """

        for projectile in Weapon.projectiles:
            projectile = projectile.copy()
            projectile.place(firer=Weapon.owner, friendly=Weapon.owner.inverted)

class FireConstantly(FireBehavior):
    """Causes the ship to fire as often as possible.
    """

    def update(self, now, elapsed):
        for weapon in self.weapons:
            if not weapon.is_firing:
                weapon.start_firing()

class FireAtPlayer(FireConstantly):
    """Causes the ship to fire at the player
    """

    def FireWeapon(self, Weapon):
        player_ship = astro.keys.PLAYER_SHIP

        mode = 2
        dx = player_ship.x - self.ship.x
        dy = player_ship.y - self.ship.y
        d = magnitude(dx, dy)
        phi = math.atan2(dx, dy)

        for projectile in Weapon.projectiles:
            angle = lead_target(self.ship.x, self.ship.y,
                player_ship.x, player_ship.y,
                self.ship.speedx, self.ship.speedy,
                player_ship.speedx, player_ship.speedy,
                projectile.speed, 2, projectile.relative_to_firer_velocity)

            projectile = projectile.copy()
            angle = math.degrees(angle)
            projectile.place(firer=Weapon.owner, friendly=Weapon.owner.inverted, angle=angle)
