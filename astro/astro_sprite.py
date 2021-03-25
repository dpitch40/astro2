"""Defines a superclass for all objects that appear onscreen in the game, i.e. ships, projectiles...
"""

import os.path

import pygame

from astro import ASSET_DIR, SCREEN_SIZE, OFF_SCREEN_CUTOFF
from astro.configurable import Configurable, ConfigurableMeta
from astro.collidable import Collidable, CollidableMeta
from astro.timekeeper import Timekeeper
from astro.util import magnitude, convert_prop_x, convert_prop_y

class AstroSpriteMeta(ConfigurableMeta, CollidableMeta):
    pass

class AstroSprite(pygame.sprite.Sprite, Configurable, Timekeeper, Collidable,
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
    groups = []
    inverted = False
    confined = False

    def __init__(self, key):
        pygame.sprite.Sprite.__init__(self)
        Timekeeper.__init__(self)
        Collidable.__init__(self)
        Configurable.__init__(self, key)

        self.speedx = self.speedx_prev = 0
        self.speedy = self.speedy_prev = 0
        self.mask_rect_offsetx = 0
        self.mask_rect_offsety = 0
        self.x = 0
        self.y = 0

    def initialize(self):
        if hasattr(self, 'max_speed') and hasattr(self, 'acceleration'):
            # Calsulate stopping distance
            self.stopping_distance = (self.max_speed ** 2) / (self.acceleration * 2)

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
        if isinstance(startx, float) and startx >= 0 and startx <= 1:
            startx = convert_prop_x(startx)
        if isinstance(starty, float) and starty >= 0 and starty <= 1:
            starty = convert_prop_y(starty)
        self.rect.center = (startx, starty)
        self.speedx = speedx
        self.speedy = speedy
        self.x = self.rect.centerx
        self.y = self.rect.centery
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
        self.rect, self.mask, self.mask_rect = self.generate_rect_and_mask(self.image)

    def generate_rect_and_mask(self, image):
        rect = image.get_rect()
        mask = pygame.mask.from_surface(image)
        mask_rect = mask.get_bounding_rects()[0]
        mask_rect_offsetx = mask_rect.centerx - rect.centerx
        mask_rect_offsety = mask_rect.centery - rect.centery

        return rect, mask, mask_rect

    def destroy(self):
        """Removes this object from the game.
        """
        self.kill()

    def tick(self, now, elapsed):
        """Main function called by self.update() to update the sprite for each "tick" of the
        simulation.
        """
        self._update_velocity(elapsed)
        self.update_position(elapsed)

    def update(self):
        """Called by pygame.sprite.Group.update.
        """
        self._tick()

    def update_position(self, elapsed):
        """Called each tick; updates the sprite's position based on its velocity.
        """

        self.x += elapsed * (self.speedx + self.speedx_prev) / 2
        self.y += elapsed * (self.speedy + self.speedy_prev) / 2

        self.rect.centerx = round(self.x)
        self.rect.centery = round(self.y)

        self.update_mask_pos()
        self.check_bounds()

    def update_mask_pos(self, backwards=False):
        if backwards:
            self.rect.centerx = self.x = self.mask_rect.centerx - self.mask_rect_offsetx
            self.rect.centery = self.y = self.mask_rect.centery - self.mask_rect_offsety
        else:
            self.mask_rect.centerx = self.rect.centerx + self.mask_rect_offsetx
            self.mask_rect.centery = self.rect.centery + self.mask_rect_offsety

    def _update_velocity(self, elapsed):
        self.speedx_prev = self.speedx
        self.speedy_prev = self.speedy
        self.update_velocity(elapsed)
        if hasattr(self, 'max_speed'):
            self.clamp_speed()

    def update_velocity(self, elapsed):
        """Called each tick; updates the sprite's velocity.

        This defaults to doing nothing, e.g. for passively floating objects or dumbfired
        projectiles that don't accelerate. Controlled by player input for friendly ships
        and AI for hostile ships.
        """
        pass

    def clamp_speed(self):
        # Clamp speed to within the object's maximum speed
        speed = magnitude(self.speedx, self.speedy)
        if abs(speed) > self.max_speed:
            self.speedx = self.speedx * self.max_speed / speed
            self.speedy = self.speedy * self.max_speed / speed

    def accelerate_toward(self, elapsed, targetx, targety):
        # Accelerate towards the target velocity
        # Requires self.acceleration and self.max_speed to be defined
        dx = targetx - self.speedx
        dy = targety - self.speedy
        dv = magnitude(dx, dy)
        max_accel = self.acceleration * elapsed
        if dv < max_accel:
            self.speedx, self.speedy = targetx, targety
        else:
            self.speedx += dx * max_accel / dv
            self.speedy += dy * max_accel / dv

    def accelerate_toward_point(self, elapsed, targetx, targety, decelerate=True):
        # Move towards the target point
        # Requires self.acceleration and self.max_speed to be defined
        dx = targetx - self.x
        dy = targety - self.y

        distance = magnitude(dx, dy)
        target_speed = self.max_speed
        if decelerate:
            target_speed *= min(1.0, distance / self.stopping_distance)
        target_speedx = dx * target_speed / distance
        target_speedy = dy * target_speed / distance

        return self.accelerate_toward(elapsed, target_speedx, target_speedy)

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
