"""Implements a class for projectiles (friendly or hostile).
"""

import math

from astro.astro_sprite import AstroSprite
from astro import FRIENDLY_PROJECTILES, ENEMY_PROJECTILES
from astro.timekeeper import Timekeeper

class Projectile(AstroSprite, Timekeeper):
    """A projectile fired by a weapon.
    """

    required_fields = ('imagepath', 'speed', 'damage')
    defaults = {"angle": 0}

    def place(self, firer, friendly):
        self.firer = firer
        # TODO: Base inversion on direction rather than friendly status
        # Also support facing right/left
        # Also firing from hardpoint positions and not the center of the firer
        self.inverted = friendly
        self.groups = [FRIENDLY_PROJECTILES] if friendly else [ENEMY_PROJECTILES]
        super().place(firer.rect.centerx, firer.rect.centery,
                      speedx=math.sin(math.radians(self.angle)) * self.speed,
                      speedy=math.cos(math.radians(self.angle)) * self.speed * (-1 if friendly else 1))


