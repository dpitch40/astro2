from tests import ProjectileTest as Projectile

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
    assert proj_from_static_firer.speedx == 0
    assert proj_from_static_firer.speedy == -500

    proj_from_moving_firer = Projectile.create(config={'speed': 500,
                                                       'firer_kwargs': {'speedx': 100,
                                                                        'speedy': 100}})
    assert proj_from_moving_firer.speedx == 100
    assert proj_from_moving_firer.speedy == -400
