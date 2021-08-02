import math
import random

import astro
from astro.configurable import Configurable
from astro.util import magnitude
from astro import FRIENDLY_SHIPS, ENEMY_SHIPS

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
            projectile.place(self.ship.screen, firer=Weapon.owner, friendly=Weapon.owner.inverted)

class FireNever(FireBehavior):
    """Causes the ship to fire as never as possible.
    """

    def update(self, now, elapsed):
        for weapon in self.weapons:
            if weapon.is_firing:
                weapon.stop_firing()

class FireConstantly(FireBehavior):
    """Causes the ship to fire as often as possible.'
    """

    def update(self, now, elapsed):
        for weapon in self.weapons:
            if not weapon.is_firing:
                weapon.start_firing()

class FireAtPlayer(FireConstantly):
    """Causes the ship to fire at the player
    """

    def FireWeapon(self, weapon):
        friendly = FRIENDLY_SHIPS.has(weapon.owner)
        # Target a random ship from the opposing side
        target_group = ENEMY_SHIPS if friendly else FRIENDLY_SHIPS
        target_ship = random.choice(target_group.sprites())

        mode = 2
        dx = target_ship.x - self.ship.x
        dy = target_ship.y - self.ship.y
        d = magnitude(dx, dy)
        phi = math.atan2(dx, dy)

        for projectile in weapon.projectiles:
            angle = self.ship.lead_target(target_ship.x, target_ship.y,
                target_ship.speedx, target_ship.speedy,
                projectile.speed, 2, projectile.relative_to_firer_velocity)

            projectile = projectile.copy()
            angle = math.degrees(angle)
            projectile.place(self.ship.screen, firer=weapon.owner, friendly=friendly, angle=angle)
