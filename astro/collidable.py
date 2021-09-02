import math

import pygame

from astro import logger, MAX_FPS, BOUNCINESS_MULT, COLLISION_DAMAGE_MULT, COLLIDABLE_PAIRS
from astro.util import magnitude, angle_distance, binary_search

_collidable_class_lookup = dict()

class CollidableMeta(type):
    """Metaclass for Collidable and its subclasses that initializes them in the lookup systems.
    """
    def __init__(self, *args, **kwargs):
        type.__init__(self, *args, **kwargs)
        _collidable_class_lookup[self.__name__] = self
        self.collidable_superclasses = list(self._collidable_superclasses())

    def _collidable_superclasses(self):
        yield self
        for base in self.__bases__:
            if isinstance(base, CollidableMeta) and base is not Collidable:
                yield base
                yield from base._collidable_superclasses()

class Collidable(metaclass=CollidableMeta):
    def collide_with(self, other, use_mask=False):
        if self is other:
            return
        this_class = self.class_name.lower()
        other_class = other.class_name.lower()
        collided = not use_mask or pygame.sprite.collide_mask(self, other)
        if collided:
            for other_class in other.collidable_superclasses:
                other_class = other_class.__name__.lower()
                if hasattr(self, f'collide_with_{other_class}'):
                    getattr(self, f'collide_with_{other_class}')(other)
                    return collided
            for this_class in self.collidable_superclasses:
                this_class = this_class.__name__.lower()
                if hasattr(other, f'collide_with_{this_class}'):
                    getattr(other, f'collide_with_{this_class}')(self)
                    return collided
            logger.warning(f'Collisions not defined between {this_class} and {other_class}')
        return collided


    def stop_colliding_with(self, other):
        if self is other:
            return
        this_class = self.class_name.lower()
        other_class = other.class_name.lower()
        for other_class in other.collidable_superclasses:
            other_class = other_class.__name__.lower()
            if hasattr(self, f'stop_colliding_with_{other_class}'):
                return getattr(self, f'stop_colliding_with_{other_class}')(other)
        for this_class in self.collidable_superclasses:
            this_class = this_class.__name__.lower()
            if hasattr(other, f'stop_colliding_with_{this_class}'):
                return getattr(other, f'stop_colliding_with_{this_class}')(self)
        # Don't log a warning if not found


    def collide_with_mass(self, other):
        # print()
        # print('Speed', self.speedx, self.speedy)
        if not (self.speedx or self.speedy or other.speedx or other.speedy):
            return

        # To compensate for limited frame rate, step back through time to the moment the masks
        # first minimally overlapped
        step = 1 / (MAX_FPS * 4)
        def pos_at_t(t):
            return self.rect.centerx + self.speedx * t, self.rect.centery + self.speedy * t
        def other_pos_at_t(t):
            return other.rect.centerx + other.speedx * t, other.rect.centery + other.speedy * t
        def get_overlap_at_t(t):
            # Calculate angle of collision
            x1, y1 = pos_at_t(t)
            x2, y2 = other_pos_at_t(t)
            return self.mask.overlap_mask(other.mask, (round(x2 - x1), round(y2 - y1)))
        T = 0
        overlap = prev_overlap = get_overlap_at_t(T)
        while overlap.count():
            T -= step
            prev_overlap = overlap
            overlap = get_overlap_at_t(T)
        overlap = prev_overlap

        # Invert angle to convert from cartesian to pixel coordinates, and add 90 degrees
        normal_angle = math.radians(90 - overlap.angle())
        # print(overlap.count(), 90 - overlap.angle())
        c1 = self.rect.center
        c2 = other.rect.center
        # Angle from other to self
        a = math.atan2(c1[1] - c2[1], c1[0] - c2[0])
        if angle_distance(normal_angle, a + math.pi, True) < angle_distance(normal_angle, a, True):
            normal_angle += math.pi
        # Angle of relative velocity
        velocity_angle = math.atan2(self.speedy - other.speedy, self.speedx - other.speedx)
        # Need to ensure the collision actually pushes the ships apart; the code will fail to
        # find a solution if it doesn't
        for angle, name in [(normal_angle, 'Normal'),
                            (a, 'Dir'),
                            (math.atan2(other.speedy - self.speedy, other.speedx - self.speedx), 'Speed')]:
            if angle_distance(angle, velocity_angle, True) > math.radians(100):
                ax = math.cos(angle)
                ay = math.sin(angle)
                # print(name)
                break
        # print(math.degrees(angle_distance(math.atan2(self.speedy, self.speedx),
        #                                   math.atan2(ay, ax), True)))
        # print('ax, ay =', ax, ay)

        # Calculate total kinetic energy
        tke = self.kinetic_energy + other.kinetic_energy

        # Find the "force" (actually average force times a short time interval) of the collision
        # using numerical methods, aiming to conserve kinetic energy (for now)
        def v1f(F):
            return self.speedx + F * ax / self.mass, self.speedy + F * ay / self.mass
        def v2f(F):
            return other.speedx - F * ax / other.mass, other.speedy - F * ay / other.mass
        def d_tke(F):
            return tke - (0.5 * self.mass * magnitude(*v1f(F)) ** 2 + \
                          0.5 * other.mass * magnitude(*v2f(F)) ** 2)
        i = 1
        while True:
            val = d_tke(2 << i)
            if val < 0:
                # print(i, d_tke(2 << (i - 1)), val)
                f = binary_search(d_tke, 2 << (i - 1), 2 << i, 1, True)
                break
            i += 1
        # print(f)
        # print('T =', T)
        # print('Before', self.x, self.y, other.x, other.y, get_overlap_at_t(0).count())

        # Adjust ships' position so they no longer overlap
        self.x, self.y = pos_at_t(T)
        self.sync_position()
        other.x, other.y = other_pos_at_t(T)
        other.sync_position()

        # Average elasticity of collision
        elasticity = (self.elasticity + other.elasticity) / 2
        # Adjust ships' velocity to bounce them off each other
        self.speedx, self.speedy = v1f(f * elasticity * BOUNCINESS_MULT)
        other.speedx, other.speedy = v2f(f * elasticity * BOUNCINESS_MULT)

        # Inflict collision damage
        damage = f * (1.0 - elasticity) * COLLISION_DAMAGE_MULT
        # Multiplier to make heavier ships sustain less damage and lighter ships more
        mass_mult = other.mass / self.mass

        self.damage(max(damage * mass_mult, 1))
        other.damage(max(damage / mass_mult, 1))
        print(f"Your damage (ono D:): {min(damage * mass_mult, 1)} Their Damage (ayy poggers :D): {min(damage / mass_mult, 1)}")

        # print('After', self.x, self.y, other.x, other.y, get_overlap_at_t(0).count())
        # print(self.speedx, self.speedy)
        # if self.__class__.__name__ == 'Shield':
        #     print(self.rect.center, self.owner.x, self.owner.y, self.owner.rect.center)
        # print(other.speedx, other.speedy)
        # print(self, other)

colliding_pairs = set()

def check_collisions():
    collided_this_frame = set()

    for group1, group2, use_mask in COLLIDABLE_PAIRS:
        for sprite, colliders in pygame.sprite.groupcollide(group1, group2, False, False).items():
            for collider in colliders:
                collided = sprite.collide_with(collider, use_mask)
                if collided:
                    if sprite.alive() and collider.alive():
                        # Track the collision
                        collided_this_frame.add((sprite, collider))
                        colliding_pairs.add((sprite, collider))
                    else:
                        # Stop tracking the collision if at least one object is dead
                        colliding_pairs.discard((sprite, collider))

    no_longer_colliding = colliding_pairs - collided_this_frame
    for sprite, collider in no_longer_colliding:
        sprite.stop_colliding_with(collider)
        colliding_pairs.discard((sprite, collider))
