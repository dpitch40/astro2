from io import StringIO
from unittest.mock import patch

import pytest

from astro.configurable import Configurable, load_from_yaml

class ShipTest(Configurable):
    pass

class WeaponTest(Configurable):
    pass

class ProjectileTest(Configurable):
    defaults = {'angle': 0}


def test_configurable():
    projectile_data = """---
ProjectileTest[Bullet]:
    speed: 2000
    damage: 5
ProjectileTest[Bomb]:
    speed: 200
    damage: 50
"""

    weapon_data = """---
WeaponTest[Chaingun]:
    rate_of_fire: 10.0
    projectiles:
        - ProjectileTest[Bullet]
WeaponTest[HeavyChaingun]:
    rate_of_fire: 10.0
    projectiles:
        - ProjectileTest(Bullet):
            damage: 7
WeaponTest[Bombs]:
    rate_of_fire: 0.5
    projectiles:
        - ProjectileTest[Bomb]
        - ProjectileTest[Bomb]
"""

    ship_data = """---
ShipTest[Fighter]:
    max_speed: 500
    acceleration: 1000
    HP: 100
    weapons:
        - WeaponTest[HeavyChaingun]
ShipTest[Bomber]:
    max_speed: 300
    acceleration: 500
    HP: 300
    weapons:
        - WeaponTest[Chaingun]
        - WeaponTest[Chaingun]
        - WeaponTest[Bombs]
"""

    projectiles = load_from_yaml(StringIO(projectile_data))
    weapons = load_from_yaml(StringIO(weapon_data))
    ships = load_from_yaml(StringIO(ship_data))

    assert projectiles['Bullet'].speed == 2000
    assert projectiles['Bullet'].damage == 5
    assert projectiles['Bomb'].speed == 200
    assert projectiles['Bomb'].damage == 50

    assert weapons['Chaingun'].rate_of_fire == 10.0
    assert weapons['Chaingun'].projectiles[0] is projectiles['Bullet']
    assert weapons['HeavyChaingun'].rate_of_fire == 10.0
    assert weapons['HeavyChaingun'].projectiles[0] is not projectiles['Bullet']
    assert weapons['HeavyChaingun'].projectiles[0].speed == 2000
    assert weapons['HeavyChaingun'].projectiles[0].damage == 7
    assert weapons['Bombs'].rate_of_fire == 0.5
    assert weapons['Bombs'].projectiles[0] is projectiles['Bomb']
    assert weapons['Bombs'].projectiles[1] is projectiles['Bomb']

    assert ships['Fighter'].max_speed == 500
    assert ships['Fighter'].acceleration == 1000
    assert ships['Fighter'].HP == 100
    assert ships['Fighter'].weapons[0] is weapons['HeavyChaingun']
    assert ships['Bomber'].max_speed == 300
    assert ships['Bomber'].acceleration == 500
    assert ships['Bomber'].HP == 300
    assert ships['Bomber'].weapons[0] is weapons['Chaingun']
    assert ships['Bomber'].weapons[1] is weapons['Chaingun']
    assert ships['Bomber'].weapons[2] is weapons['Bombs']

def test_copying():
    weapon_data = """---
WeaponTest[Chaingun2]:
    rate_of_fire: 10.0
    projectiles:
      - ProjectileTest(Bullet):
          damage: 7
"""
    chaingun = load_from_yaml(StringIO(weapon_data))
    assert chaingun.projectiles[0].damage == 7
    assert chaingun.projectiles[0].angle == 0

    copied_proj = chaingun.projectiles[0].copy(angle=-15)
    assert copied_proj.damage == 7
    assert copied_proj.angle == -15

class Triangle(Configurable):
    required_fields = ('side1', 'side2', 'side3')

    def perimeter(self):
        return self.side1 + self.side2 + self.side3

class TriangleDefaults(Triangle):
    defaults = {'side1': 1, 'side2': 1, 'side3': 1}

def test_required_fields():
    tri_data = """---
Triangle[ABC]:
    side1: 2
"""
    with pytest.raises(RuntimeError):
        abc = load_from_yaml(StringIO(tri_data))

def test_fields():
    tri_data = """---
TriangleDefaults[ABC]:
    side1: 2
"""
    abc = load_from_yaml(StringIO(tri_data))
    assert abc.perimeter() == 4
    assert TriangleDefaults.instance('ABC') is abc
    assert TriangleDefaults.instance('ABC', side3=4) is abc
    def_ = TriangleDefaults.instance('ABC', copy=True, side1=3, side2=2)
    assert def_ is not abc
    assert def_.perimeter() == 6

def test_anonymous_config():
    data = """---
ShipTest[Fighter2]:
    max_speed: 500
    acceleration: 1000
    HP: 100
    weapons:
        - WeaponTest():
            rate_of_fire: 11.0
            projectiles:
                - ProjectileTest[]:
                      speed: 2000
                      damage: 7
"""
    fighter = load_from_yaml(StringIO(data))
    assert fighter.weapons[0].rate_of_fire == 11.0
    assert len(fighter.weapons[0].projectiles) == 1
    assert fighter.weapons[0].projectiles[0].damage == 7
