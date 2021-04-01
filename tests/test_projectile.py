import math

from tests import ProjectileTest as Projectile, PlayerShipTest as PlayerShip

def test_that_slow_projectiles_still_move():

    fast_proj = Projectile.create(config={'speed': 500})
    fast_proj_start_pos = fast_proj.rect.center
    for i in range(60):
        fast_proj.tick(0, 1/60)

    slow_proj = Projectile.create(config={'speed': 2})
    slow_proj_start_pos = slow_proj.rect.center
    for i in range(60):
        slow_proj.tick(0, 1/60)

    assert fast_proj_start_pos != fast_proj.rect.center
    assert slow_proj_start_pos != slow_proj.rect.center

def test_that_projectile_speed_is_relative_to_firer():
    proj_from_static_firer = Projectile.create(config={'speed': 500})
    assert round(proj_from_static_firer.speedx) == 0
    assert round(proj_from_static_firer.speedy) == -500

    proj_from_moving_firer = Projectile.create(config={'speed': 500,
                                                       'firer_kwargs': {'speedx': 100,
                                                                        'speedy': 100}})
    assert round(proj_from_moving_firer.speedx) == 100
    assert round(proj_from_moving_firer.speedy) == -400

def test_collision_between_projectile_and_ship():
    proj = Projectile.create(config={'speed': 500,
                                     'damage': 1})
    target_ship = PlayerShip.create(config={'max_hp': 10})

    assert target_ship.hp == 10
    assert proj.alive()
    assert target_ship.alive()

    target_ship.collide_with(proj)
    assert target_ship.hp == 9
    assert not proj.alive()

    for i in range(9):
        assert target_ship.alive()
        proj = Projectile.create(config={'speed': 500,
                                         'damage': 1})
        target_ship.collide_with(proj)
    assert not target_ship.alive()
