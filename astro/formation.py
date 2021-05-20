"""
Different shapes--box, grid, zigzag
Override update_velocity for complex coordinated movements like moving in a circle
"""

import operator
import random
import collections
import time

import pygame

from astro import OBJECTS
from astro.configurable import Configurable
from astro.movable import Movable
from astro.astro_sprite import AstroSprite
from astro.util import magnitude
from astro.move_behavior import MoveBehavior
from astro.image import generate_rect_and_mask

# class Formation(Configurable, Movable):
class Formation(AstroSprite):
    required_fields = ('ships', 'width', 'height')
    extra_copy_fields = ['blank_move_behavior']
    defaults = {'move_behavior': None,
                'fire_behavior': None,
                'center_x': None}
    groups = [OBJECTS]

    def __init__(self, key):
        # Movable.__init__(self)
        # Configurable.__init__(self, key)
        super().__init__(key)

        self.center = None
        self._num_ships = None
        self.more_ships = None

    def load_image(self):
        radius = 16
        image = pygame.Surface((radius,radius))
        color = (0, 255, 0)
        pygame.draw.circle(image, color, (radius/2, radius/2), radius/2)
        image.convert()
        self.image = image

        self.rect, self.mask, self.mask_rect, self.mask_rect_offsetx, \
            self.mask_rect_offsety, self.mask_centroid = generate_rect_and_mask(self.image)

    def calculate_ship_offset(self, ship, i):
        raise NotImplementedError

    def calculate_spawn_offsets(self):
        # Calculate offsets relative to formation center for all ships
        self.ship_offsets = list()
        spawn_offsets = list()
        for i, ship in enumerate(self.more_ships):
            offsetx, offsety = self.calculate_ship_offset(ship, i)
            self.ship_offsets.append((offsetx, offsety))
            ship.move_behavior.formation = self
            ship.move_behavior.formation_i = i
            # y position of the formation at which to spawn the ship
            spawn_offset = -ship.rect.height // 2 - offsety
            spawn_offsets.append((spawn_offset, ship, i))
        # Will be a deque of (offset, ship) 2-tuples in increasing offset order
        self.spawn_offsets = collections.deque(sorted(spawn_offsets, key=operator.itemgetter(0)))

    def deploy(self, screen):
        """Like place, for formations.

        Spawns all ships in the formation and starts moving them according to configuration.
        """
        self.place(screen, self.center_x, self.height // -2, 0, 0)
        self.move_behavior.init_ship(self)
        self.deployed = time.time()
        self.calculate_spawn_offsets()

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self.width, self.height = self.screen.convert_proportional_coordinates(self.width, self.height)

    def _expand_ships(self):
        ships = list()
        for ship, count in self.ships:
            for i in range(count):
                ships.append(ship.copy())

        random.shuffle(ships)
        return ships

    def initialize(self):
        if not hasattr(self, 'dest_y'):
            self.dest_y = self.height // 2
        self.more_ships = self._expand_ships()
        self.acceleration = min(map(operator.attrgetter('acceleration'), self.more_ships))
        self.max_speed = min(map(operator.attrgetter('max_speed'), self.more_ships))
        if not hasattr(self, 'blank_move_behavior'):
            self.blank_move_behavior = self.move_behavior is None
        if self.blank_move_behavior:
            # Initialize blank move behavior to get us onscreen
            self.move_behavior = MoveBehavior.instance('move_on_screen', True,
                initial_dest=(self.center_x, self.dest_y))
        self._reached_dest = False

        self.speedx, self.speedy = 0, 0
        if self.center_x is None:
            self.center_x = 1/2
        self.to_be_deployed = self.num_ships
        # Movable.initialize(self)
        super().initialize()

    @property
    def num_ships(self):
        if self._num_ships is None:
            if self.more_ships is not None:
                self._num_ships = len(self.more_ships)
            else:
                self._num_ships = sum(c for s, c in self.ships)
        return self._num_ships

    @property
    def ships_remaining(self):
        return self.to_be_deployed + len([s for s in self.more_ships if s.alive()])

    def tick(self, now, elapsed):
        super().tick(now, elapsed)
        # Spawn ships
        while self.spawn_offsets and self.spawn_offsets[0][0] < self.y:
            _, ship, i = self.spawn_offsets.popleft()
            offsetx, offsety = self.ship_offsets[i]
            ship.place(self.screen, round(self.x + offsetx), round(self.y + offsety), self.speedx, self.speedy)
            self.to_be_deployed -= 1

        if self.blank_move_behavior:
            if not self._reached_dest and \
                self.move_behavior.reached_dest(*self.move_behavior.initial_dest):

                self._reached_dest = True
                for i, ship in enumerate(self.more_ships):
                    ship.move_behavior.formation = None
                    ship.move_behavior.formation_i = None
            if self._reached_dest:
                self.accelerate_toward(elapsed, 0, 0)

    def update_ship_velocity(self, elapsed, ship, i):
        # Keep ship in sync with formation
        ship.accelerate_toward(elapsed, self.speedx, self.speedy)

class Grid(Formation):
    required_fields = Formation.required_fields + ('rows', 'columns',)

    def calculate_ship_offset(self, ship, i):
        row, col = divmod(i, self.columns)
        if row == self.rows - 1 and self.num_ships < self.num_slots:
            row_length = self.num_ships % self.columns
        else:
            row_length = self.columns

        if row_length > 1:
            x = -self.width / 2
            x += (col / (row_length - 1)) * self.width
        else:
            x = 0

        if self.rows > 1:
            y = -self.height / 2
            y += (row / (self.rows - 1)) * self.height
        else:
            y = 0
        return x, y

    def initialize(self):
        self.num_slots = self.rows * self.columns
        if self.num_ships > self.num_slots:
            raise ValueError(f'Grid has {self.num_ships} ships and only {self.num_slots} slots')
        self.column_spacing = 100 if self.columns < 2 else self.width / (self.columns - 1)
        self.row_spacing = 100 if self.rows < 2 else self.height / (self.rows - 1)
        super().initialize()

class Line(Grid):
    required_fields = Formation.required_fields

    def initialize(self):
        self.rows, self.columns = 1, self.num_ships
        super().initialize()
