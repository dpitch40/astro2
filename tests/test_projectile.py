from unittest.mock import patch, Mock

import pygame

from astro.projectile import Projectile
from astro.ship import Ship
from astro import SCREEN_SIZE


# TODO: Move this to a common module
def create_test_projectile(x=SCREEN_SIZE[0]/2, y=SCREEN_SIZE[1]/2, size=(10, 10), 
    firer_kwargs=None, **setup_kwargs):
    """Very simplified setup to create a Projectile for testing purposes.
    """
    firer_rect = pygame.Rect((x, y, 1, 1))
    if firer_kwargs is None:
        firer_kwargs = {}
    firer = Mock(rect=firer_rect, **firer_kwargs)
    friendly = setup_kwargs.pop('friendly', True)
    with patch.object(Projectile, 'load_image'):
        proj = Projectile('testproj')
        proj._setup(setup_kwargs)
        proj.rect = proj.mask_rect = pygame.Rect((0, 0) + size)
        proj.place(firer, friendly)
    return proj


def test_that_slow_projectiles_still_move():

    fast_proj = create_test_projectile(speed=500)
    fast_proj_start_pos = fast_proj.rect.center
    for i in range(60):
        fast_proj.tick(0, 1/60)

    slow_proj = create_test_projectile(speed=2)
    slow_proj_start_pos = slow_proj.rect.center
    for i in range(60):
        slow_proj.tick(0, 1/60)

    assert fast_proj_start_pos != fast_proj.rect.center
    assert slow_proj_start_pos != slow_proj.rect.center

def test_that_projectile_speed_is_relative_to_firer():
    proj_from_static_firer = create_test_projectile(speed=500)
    assert proj_from_static_firer.speedx == 0
    assert proj_from_static_firer.speedy == -500

    proj_from_moving_firer = create_test_projectile(speed=500, firer_kwargs={"speedx": 100,
                                                                             "speedy": 100})
    assert proj_from_static_firer.speedx == 100
    assert proj_from_static_firer.speedy == -400
