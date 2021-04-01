import os.path
from collections import namedtuple

import pygame

from astro import ASSET_DIR
from astro.util import frange

CachedImage = namedtuple('CachedImage',
    ['image',
     'rect',
     'mask',
     'mask_rect',
     'mask_rect_offsetx',
     'mask_rect_offsety',
     'mask_centroid'])

IMAGE_CACHE = dict()

ALLOWED_DIRECTIONS = {None, 4, 8}

def _cache_image(key, image):
    rect, mask, mask_rect, mask_rect_offsetx, mask_rect_offsety, centroid = \
        generate_rect_and_mask(image)
    t = IMAGE_CACHE[key] = CachedImage(image, rect, mask, mask_rect,
                                       mask_rect_offsetx, mask_rect_offsety, centroid)
    return t

def load_image(rel_path, flip=False, directions=None):
    if directions not in ALLOWED_DIRECTIONS:
        raise ValueError(f'Invalid number of directions: {directions}')
    key = rel_path + ('flipped' if flip else '')

    if key not in IMAGE_CACHE:
        full_path = os.path.join(ASSET_DIR, rel_path)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f'Image not found: {full_path}')

        image = pygame.image.load(full_path).convert_alpha()
        if flip:
            image = pygame.transform.flip(image, False, True)
        image_tuple = _cache_image(key, image)

        if directions is not None:
            for angle in frange(0, 360, 360 / directions):
                key = rel_path + str(round(angle))
                if angle != 0:
                    rotated_image = pygame.transform.rotate(image, angle)
                else:
                    rotated_image = image.copy()
                _cache_image(key, rotated_image)
    else:
        image_tuple = IMAGE_CACHE[key]

    image, rect, mask, mask_rect, mask_rect_offsetx, mask_rect_offsety, centroid = image_tuple
    return image, rect.copy(), mask, mask_rect.copy(), mask_rect_offsetx, mask_rect_offsety, centroid

def generate_rect_and_mask(image):
    rect = image.get_rect()
    mask = pygame.mask.from_surface(image)
    mask_rect = mask.get_bounding_rects()[0]
    mask_rect_offsetx = mask_rect.centerx - rect.centerx
    mask_rect_offsety = mask_rect.centery - rect.centery
    mask_centroid = mask.centroid()

    return rect, mask, mask_rect, mask_rect_offsetx, mask_rect_offsety, mask_centroid
