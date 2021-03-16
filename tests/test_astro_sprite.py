from tests import AstroSpriteTest as AstroSprite

def test_clamp_speed():
    sprite = AstroSprite.create(speedy=100, config={'max_speed': 100})
    assert (sprite.speedx, sprite.speedy) == (0, 100)
    sprite.clamp_speed()
    assert (sprite.speedx, sprite.speedy) == (0, 100)

    sprite = AstroSprite.create(speedy=120, config={'max_speed': 100})
    assert (sprite.speedx, sprite.speedy) == (0, 120)
    sprite.clamp_speed()
    assert (sprite.speedx, sprite.speedy) == (0, 100)

    sprite = AstroSprite.create(speedx=120, speedy=160, config={'max_speed': 100})
    assert (sprite.speedx, sprite.speedy) == (120, 160)
    sprite.clamp_speed()
    assert (sprite.speedx, sprite.speedy) == (60, 80)

def test_accelerate_toward():
    sprite = AstroSprite.create(config={'max_speed': 100,
                                        'acceleration': 50})
    assert (sprite.speedx, sprite.speedy) == (0, 0)
    sprite.accelerate_toward(0.5, 0, 100)
    assert (sprite.speedx, sprite.speedy) == (0, 25)
    sprite.accelerate_toward(0.5, 0, 100)
    assert (sprite.speedx, sprite.speedy) == (0, 50)
    sprite.accelerate_toward(1, 0, 100)
    assert (sprite.speedx, sprite.speedy) == (0, 100)
    sprite.accelerate_toward(1, 0, 150)
    assert (sprite.speedx, sprite.speedy) == (0, 150)
    sprite.clamp_speed()
    assert (sprite.speedx, sprite.speedy) == (0, 100)
    sprite.accelerate_toward(1, 0, 75)
    assert (sprite.speedx, sprite.speedy) == (0, 75)
    sprite.accelerate_toward(1, -60, -5)
    assert (sprite.speedx, sprite.speedy) == (-30, 35)

def test_update_position():
    sprite = AstroSprite.create(startx=0, starty=0)
    assert (sprite.speedx, sprite.speedy) == (0, 0)
    assert (sprite.x, sprite.y) == (0, 0)

    sprite.speedx = 8
    sprite.update_position(0.5)
    assert (sprite.x, sprite.y) == (4, 0)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (12, 0)

    sprite.speedx = -2
    sprite.speedy = 4
    sprite.update_position(0.5)
    assert (sprite.x, sprite.y) == (11, 2)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (9, 6)

    # Test rect position rounding
    sprite.speedx = -0.125
    sprite.speedy = 0
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (8.875, 6)
    assert sprite.rect.center == (9, 6)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (8.75, 6)
    assert sprite.rect.center == (9, 6)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (8.625, 6)
    assert sprite.rect.center == (9, 6)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (8.5, 6)
    assert sprite.rect.center == (8, 6)
    sprite.update_position(1.0)
    assert (sprite.x, sprite.y) == (8.375, 6)
    assert sprite.rect.center == (8, 6)

def test_accelerate_toward_point():
    sprite = AstroSprite.create(startx=0, starty=0,
                                config={'max_speed': 10,
                                        'acceleration': 5})
    assert (sprite.speedx, sprite.speedy) == (0, 0)
    sprite.accelerate_toward_point(1, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (5, 0)
    sprite.update_position(1)
    assert (sprite.x, sprite.y) == (5, 0)

    sprite.accelerate_toward_point(1, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (10, 0)
    sprite.update_position(1)
    assert (sprite.x, sprite.y) == (15, 0)

    sprite.accelerate_toward_point(1, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (10, 0)
    sprite.update_position(1)
    assert (sprite.x, sprite.y) == (25, 0)

    sprite.update_position(1) # 35
    sprite.update_position(1) # 45
    sprite.update_position(1) # 55
    sprite.update_position(1) # 65
    sprite.update_position(1) # 75
    sprite.update_position(1) # 85

    sprite.accelerate_toward_point(1, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (10, 0)
    sprite.update_position(0.5)
    assert (sprite.x, sprite.y) == (90, 0)

    sprite.accelerate_toward_point(0.5, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (10, 0)
    sprite.update_position(0.5)
    assert (sprite.x, sprite.y) == (95, 0)

    sprite.accelerate_toward_point(1, 100, 0)
    assert (sprite.speedx, sprite.speedy) == (5, 0)
