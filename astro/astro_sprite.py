"""Defines a superclass for all objects that appear onscreen in the game, i.e. ships, projectiles...
"""

import os.path

import pygame

from astro import ASSET_DIR, SCREEN_SIZE, OFF_SCREEN_CUTOFF
from astro.configurable import Configurable
from astro.timekeeper import Timekeeper

class AstroSprite(pygame.sprite.Sprite, Configurable, Timekeeper):
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
    groups = []
    inverted = False
    confined = False

    def __init__(self, key):
        pygame.sprite.Sprite.__init__(self)
        Timekeeper.__init__(self)
        Configurable.__init__(self, key)

    def place(self, startx, starty, speedx=0, speedy=0):
        """Adds this object to the game at the specified location.

        Can optionally specify an initial speed. Also adds it to its sprite groups.

        Args:
            startx (int): The starting x-coordinate.
            starty (int): The starting y-coordinate.
            speedx (optional int): The starting horizontal speed. Defaults to 0.
            speedy (optional int): The starting vertical speed. Defaults to 0.
        """
        self.load_image()
        self.rect.center = (startx, starty)
        self.speedx = speedx
        self.speedy = speedy
        self.add(self.groups)

    def _load_image(self, rel_path):
        """Backend method for loading an image, inverting it if appropriate, and converting it.
        """
        full_path = os.path.join(ASSET_DIR, rel_path)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f'Image not found: {full_path}')

        image = pygame.image.load(full_path)
        if self.inverted:
            image = pygame.transform.flip(image, False, True)
        return image.convert_alpha()

    def load_image(self):
        """Loads the image file for this object and initializes its image and rectangle
            attributes as expected by pygame.sprite.Sprite.
        """
        # TODO: Create images for all four facing directions
        # TODO: Cache images in memory to avoid reloading them every time
        self.image = self._load_image(self.imagepath)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_rect = self.mask.get_bounding_rects()[0]
        self.mask_rect_offsetx = self.mask_rect.centerx - self.rect.centerx
        self.mask_rect_offsety = self.mask_rect.centery - self.rect.centery

    def collide(self, collider):
        """Handles collisions between this sprite and another sprite.

        Args:
            collider: The sprite this sprite collided with.
        """
        # TODO
        pass

    def destroy(self):
        """Removes this object from the game.
        """
        self.kill()

    def tick(self, now, elapsed):
        """Main function called by self.update() to update the sprite for each "tick" of the
        simulation.
        """
        self.update_velocity(elapsed)
        self.update_position(elapsed)

    def update(self):
        """Called by pygame.sprite.Group.update.
        """
        self._tick()

    def update_position(self, elapsed):
        """Called each tick; updates the sprite's position based on its velocity.
        """
        self.rect.centerx += elapsed * self.speedx
        self.rect.centery += elapsed * self.speedy
        self.update_mask_pos()

        self.check_bounds()

    def update_mask_pos(self, backwards=False):
        if backwards:
            self.rect.centerx = self.mask_rect.centerx - self.mask_rect_offsetx
            self.rect.centery = self.mask_rect.centery - self.mask_rect_offsety
        else:
            self.mask_rect.centerx = self.rect.centerx + self.mask_rect_offsetx
            self.mask_rect.centery = self.rect.centery + self.mask_rect_offsety

    def update_velocity(self, elapsed):
        """Called each tick; updates the sprite's velocity.

        This defaults to doing nothing, e.g. for passively floating objects or dumbfired
        projectiles that don't accelerate. Controlled by player input for friendly ships
        and AI for hostile ships.
        """
        pass

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
            elif self.mask_rect.right > SCREEN_SIZE[0]:
                self.mask_rect.right = SCREEN_SIZE[0]
                if self.speedx > 0:
                    self.speedx = 0

            if self.mask_rect.top < 0:
                self.mask_rect.top = 0
                if self.speedy < 0:
                    self.speedy = 0
            elif self.mask_rect.bottom > SCREEN_SIZE[1]:
                self.mask_rect.bottom = SCREEN_SIZE[1]
                if self.speedy > 0:
                    self.speedy = 0
            self.update_mask_pos(True)
        else:
            # Destroy the sprite if it goes too far offscreen
            if self.mask_rect.centerx < -OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centerx > SCREEN_SIZE[0] + OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centery < -OFF_SCREEN_CUTOFF:
                self.destroy()
            elif self.mask_rect.centery > SCREEN_SIZE[1] + OFF_SCREEN_CUTOFF:
                self.destroy()
