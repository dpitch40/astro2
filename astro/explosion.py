import time
import math

import pygame

from astro import EXPLOSIONS, EXPLOSION_SIZE_SCALE, EXPLOSION_DURATION_SCALE
from astro.image import generate_rect_and_mask
from astro.astro_sprite import AstroSprite

class Explosion(AstroSprite):
    groups = [EXPLOSIONS]

    def __init__(self, exploding_object):
        super().__init__(None)

        self.exploding_object = exploding_object
        self.start_time = time.time()
        self.max_age = math.sqrt(self.exploding_object.mass) * EXPLOSION_DURATION_SCALE / 25
        self.max_radius = math.pow(self.exploding_object.mass, 0.33) * EXPLOSION_SIZE_SCALE * 7.5

        self.init_sprite()

    def init_sprite(self):
        self.image = pygame.Surface((2 * self.max_radius, 2 * self.max_radius)).convert_alpha()
        self.update_sprite(time.time())
        self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
            self.mask_rect_offsety, self.mask_centroid = generate_rect_and_mask(self.image)

    def tick(self, now, elapsed):
        self.update_sprite(now)

    def update_sprite(self, now):
        age_proportion = (now - self.start_time) / self.max_age
        if age_proportion > 1:
            self.destroy()
        else:
            self.image.fill((0, 0, 0, 0))
            radius = self.max_radius * age_proportion
            alpha = 255 * (1 - age_proportion)
            color = (255, 255 * (1 - age_proportion), 0, alpha)
            pygame.draw.circle(self.image, color, (self.max_radius, self.max_radius), radius)

