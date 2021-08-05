import pygame

from astro import FRONT_VFX, BACK_VFX
from astro.astro_sprite import FollowSprite
from astro.image import generate_rect_and_mask

class VFX(FollowSprite):
    required_fields = FollowSprite.required_fields + ('above',)

    def place(self, screen, owner):
        self.groups = [FRONT_VFX] if self.above else [BACK_VFX]
        super().place(screen, owner)

class CircleVFX(VFX):
    defaults = VFX.defaults.copy()
    defaults.update({'color': (180, 180, 255),
                     'alpha': 128,
                     'imagepath': None,
                     'size_delta': 0})

    deferred_image_load = True

    def _load_image(self, *args, **kwargs):
        sizex, sizey = self.owner.rect.size
        sizex += self.size_delta
        sizey += self.size_delta
        image = pygame.Surface((sizex, sizey), flags=pygame.SRCALPHA)
        color = tuple(self.color) + (self.alpha,)
        pygame.draw.ellipse(image, color, image.get_rect())
        return (image,) + generate_rect_and_mask(image)