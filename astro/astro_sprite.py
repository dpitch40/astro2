"""Defines a superclass for all objects that appear onscreen in the game, i.e. ships, projectiles...
"""

import pygame

from astro import OFF_SCREEN_CUTOFF
from astro.image import load_image
from astro.configurable import Configurable, ConfigurableMeta
from astro.collidable import Collidable, CollidableMeta
from astro.movable import Movable
from astro.util import magnitude

class AstroSpriteMeta(ConfigurableMeta, CollidableMeta):
    def __init__(self, *args, **kwargs):
        ConfigurableMeta.__init__(self, *args, **kwargs)
        CollidableMeta.__init__(self, *args, **kwargs)

class AstroSprite(Configurable, Movable, Collidable, pygame.sprite.Sprite,
    metaclass=AstroSpriteMeta):
    """Class for any object that is rendered onscreen in the game.

    Attributes:
        confined (bool): If True, the object will be confined to the bounds of the screen and
            unable to move past them. If False, it can travel beyond the screen boundaries, but will
            be automatically destroyed if it moves too far offscreen.
        groups (list of pygame.sprite.Group): List of sprite groups this object should belong to.
        imagepath (str): Path to the object's sprite image file, within the assets directory.
        inverted (bool): Set to True for friendly ships and projectiles. Inverts the sprite.
    """
    required_fields = ('imagepath',)
    defaults = {'elasticity': 0.5}
    groups = []
    inverted = False
    confined = False
    deferred_image_load = False

    def __init__(self, key):
        pygame.sprite.Sprite.__init__(self)
        Movable.__init__(self)
        Collidable.__init__(self)
        Configurable.__init__(self, key)

        self.speedx = self.speedx_prev = 0
        self.speedy = self.speedy_prev = 0
        self.mask_rect_offsetx = 0
        self.mask_rect_offsety = 0
        self.x = 0
        self.y = 0
        self.follow_sprites = set()

    def initialize(self):
        Movable.initialize(self)
        if not self.deferred_image_load:
            self.load_image()

    def place(self, screen, startx, starty, speedx=0, speedy=0, absolute_coords=False):
        """Adds this object to the game at the specified location.

        Can optionally specify an initial speed. Also adds it to its sprite groups.

        Args:
            startx (int): The starting x-coordinate.
            starty (int): The starting y-coordinate.
            speedx (optional int): The starting horizontal speed. Defaults to 0.
            speedy (optional int): The starting vertical speed. Defaults to 0.
        """
        super().place(screen, startx, starty, speedx, speedy, absolute_coords)
        if self.deferred_image_load:
            self.load_image()
        self.rect.center = self.x ,self.y = round(self.x), round(self.y)
        self.add(*self.groups)

    def _load_image(self, *args, **kwargs):
        return load_image(*args, **kwargs)

    def load_image(self):
        """Loads the image file for this object and initializes its image and rectangle
            attributes as expected by pygame.sprite.Sprite.
        """
        self.image, self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
            self.mask_rect_offsety, self.mask_centroid = self._load_image(self.imagepath, self.inverted)

    def destroy(self):
        """Removes this object from the game.
        """
        self.kill()
        for sprite in list(self.follow_sprites):
            sprite.destroy()

    def update_position(self, elapsed):
        """Called each tick; updates the sprite's position based on its velocity.
        """

        super().update_position(elapsed)
        self.sync_position()
        self.check_bounds()

    def sync_position(self):
        self.rect.centerx = round(self.x)
        self.rect.centery = round(self.y)

        self.update_mask_pos()

    def update_mask_pos(self, backwards=False):
        if backwards:
            self.rect.centerx = self.x = self.mask_rect.centerx - self.mask_rect_offsetx
            self.rect.centery = self.y = self.mask_rect.centery - self.mask_rect_offsety
        else:
            self.mask_rect.centerx = self.rect.centerx + self.mask_rect_offsetx
            self.mask_rect.centery = self.rect.centery + self.mask_rect_offsety

    def check_bounds(self):
        """Checks the object's position in relation to the screen edge.

        For confined sprites, clamps them to within the screen boundaries.

        For non-confined sprites, destroys them if they move too far offscreen.
        """

        if self.confined:
            # Prevent the sprite from leaving the screen
            if self.mask_rect.left < 0:
                self.mask_rect.left = 0
                if self.speedx < 0:
                    self.speedx = 0
                self.update_mask_pos(True)
            elif self.mask_rect.right > self.screen_size[0]:
                self.mask_rect.right = self.screen_size[0]
                if self.speedx > 0:
                    self.speedx = 0
                self.update_mask_pos(True)

            if self.mask_rect.top < 0:
                self.mask_rect.top = 0
                if self.speedy < 0:
                    self.speedy = 0
                self.update_mask_pos(True)
            elif self.mask_rect.bottom > self.screen_size[1]:
                self.mask_rect.bottom = self.screen_size[1]
                if self.speedy > 0:
                    self.speedy = 0
                self.update_mask_pos(True)
        else:
            # Destroy the sprite if it goes too far offscreen
            if self.mask_rect.centerx < -OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centerx > self.screen_size[0] + OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centery < -OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centery > self.screen_size[1] + OFF_SCREEN_CUTOFF:
                self.destroy()

class FollowSprite(AstroSprite):
    """Subclass for sprites that follow others sprites to be rendered over/under them.

    Attributes:
        confined (bool): If True, the object will be confined to the bounds of the screen and
            unable to move past them. If False, it can travel beyond the screen boundaries, but will
            be automatically destroyed if it moves too far offscreen.
        groups (list of pygame.sprite.Group): List of sprite groups this object should belong to.
        imagepath (str): Path to the object's sprite image file, within the assets directory.
        inverted (bool): Set to True for friendly ships and projectiles. Inverts the sprite.
    """

    def place(self, screen, owner):
        self.owner = owner
        self.owner.follow_sprites.add(self)
        super().place(screen, owner.x, owner.y, owner.speedx, owner.speedy, True)

    def destroy(self):
        super().destroy()
        self.remove()

    def remove(self):
        self.owner.follow_sprites.remove(self)

    # Position and velocity mirror the owner's
    @property
    def x(self):
        return self.owner.x
    @x.setter
    def x(self, value):
        if hasattr(self, 'owner'):
            self.owner.x = value

    @property
    def y(self):
        return self.owner.y
    @y.setter
    def y(self, value):
        if hasattr(self, 'owner'):
            self.owner.y = value

    @property
    def speedx(self):
        return self.owner.speedx
    @speedx.setter
    def speedx(self, value):
        if hasattr(self, 'owner'):
            self.owner.speedx = value

    @property
    def speedy(self):
        return self.owner.speedy
    @speedy.setter
    def speedy(self, value):
        if hasattr(self, 'owner'):
            self.owner.speedy = value

    def tick(self, now, elapsed):
        # Don't update velocity, only position
        self.update_position(elapsed)

    def sync_position(self):
        super().sync_position()
        self.owner.sync_position()

    def update_position(self, elapsed):
        # Keep shield centered on owner ship
        self.rect.center = self.owner.rect.center
