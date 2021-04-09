import math

import astro.keys
from astro.configurable import Configurable
from astro.util import magnitude

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
        if mode == 0:
            # Don't compensate for velocity
            dxprime = 0
            dyprime = 0
        elif mode == 1:
            # Compensate for the firing ship's velocity
            dxprime = self.ship.speedx
            dyprime = self.ship.speedy
        else:
            # Compensate for both ship's velocity (lead the target)
            dxprime = self.ship.speedx - player_ship.speedx
            dyprime = self.ship.speedy - player_ship.speedy
        d = magnitude(dx, dy)
        phi = math.atan2(dx, dy)

        for projectile in Weapon.projectiles:
            a = (dy * dxprime - dx * dyprime) / (d * projectile.speed)
            if a > 1:
                a = 1
            elif a < -1:
                a = -1
            angle = math.degrees(phi - math.asin(a))

            projectile = projectile.copy()
            projectile.place(firer=Weapon.owner, friendly=Weapon.owner.inverted, angle=angle)
