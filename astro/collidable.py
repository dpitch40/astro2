import pygame

from astro import logger

_collidable_class_lookup = dict()

class CollidableMeta(type):
    """Metaclass for Collidable and its subclasses that initializes them in the lookup systems.
    """
    def __new__(cls, name, bases, namespace):
        # Instantiate the new class
        result = type.__new__(cls, name, bases, dict(namespace))
        # Add it to the Collidable (sub)class lookup dict
        _collidable_class_lookup[name] = result
        return result

class Collidable(metaclass=CollidableMeta):
    def collide_with(self, other, use_mask=False):
        this_class = self.class_name.lower()
        other_class = other.class_name.lower()
        if not use_mask or pygame.sprite.collide_mask(self, other):
            if hasattr(self, f'collide_with_{other_class}'):
                return getattr(self, f'collide_with_{other_class}')(other)
            elif hasattr(other, f'collide_with_{this_class}'):
                return getattr(other, f'collide_with_{this_class}')(self)
            else:
                logger.warning(f'Collisions not defined between {this_class} and {other_class}')
