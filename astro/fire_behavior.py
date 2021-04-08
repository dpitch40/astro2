from astro.configurable import Configurable

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

    def FireWeapon(self):
        for projectile in Weapon.projectiles:
            projectile = projectile.copy()
            projectile.place(firer=Weapon.owner, friendly=Weapon.owner.inverte)
