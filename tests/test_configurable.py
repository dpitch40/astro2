from io import StringIO
from unittest.mock import patch

import pytest

from astro.configurable import Configurable, load_from_yaml, check_for_undefined_objects

class Person(Configurable):
    pass

class Triangle(Configurable):
    defaults = {'side1': 1, 'side2': 1, 'side3': 1}

    def perimeter(self):
        return self.side1 + self.side2 + self.side3

def test_configurable():
    john_data = """---
Person[John]:
    name: John Smith
    age: 31
    hands:
        - left
        - right
    legs: [left, right]
    spouse: Person[Mary]
    children:
        - Person[Abby]
        - Person[Billy]
"""

    mary_data = """---
Person[Mary]:
    name: Mary Smith
    age: 31
    hands:
        - left
        - right
    legs: [left, right]
    spouse: Person[John]
    children:
        - Person[Abby]
        - Person[Billy]
"""

    abby_data = """---
Person[Abby]:
    name: Abby Smith
    age: 6
    hands:
        - left
        - right
    legs: [left, right]
    parents:
        - Person[John]
        - Person[Mary]
    siblings:
        - Person[Billy]
"""

    billy_data = """---
Person[Billy]:
    name: Billy Smith
    age: 4
    hands:
        - left
        - right
    legs: [left, right]
    parents:
        - Person[John]
        - Person[Mary]
    siblings:
        - Person[Abby]
"""
    john = load_from_yaml(StringIO(john_data))
    assert Person.instance('John') is john
    assert Person.instance('John', copy=True) is not john
    mary = load_from_yaml(StringIO(mary_data))
    assert Person.instance('Mary') is mary
    assert Person.instance('Mary', copy=True) is not mary
    abby = load_from_yaml(StringIO(abby_data))
    assert Person.instance('Abby') is abby
    assert Person.instance('Abby', copy=True) is not abby
    billy = load_from_yaml(StringIO(billy_data))
    assert Person.instance('Billy') is billy
    assert Person.instance('Billy', copy=True) is not billy

    check_for_undefined_objects()

    assert john.name == 'John Smith'
    assert john.age == 31
    assert john.hands == ['left', 'right']
    assert john.legs == ['left', 'right']
    assert john.spouse is mary
    assert john.children[0] is abby
    assert john.children[1] is billy

    assert mary.name == 'Mary Smith'
    assert mary.age == 31
    assert mary.hands == ['left', 'right']
    assert mary.legs == ['left', 'right']
    assert mary.spouse is john
    assert mary.children[0] is abby
    assert mary.children[1] is billy

    assert abby.name == 'Abby Smith'
    assert abby.age == 6
    assert abby.hands == ['left', 'right']
    assert abby.legs == ['left', 'right']
    assert abby.parents[0] is john
    assert abby.parents[1] is mary
    assert abby.siblings[0] is billy

    assert billy.name == 'Billy Smith'
    assert billy.age == 4
    assert billy.hands == ['left', 'right']
    assert billy.legs == ['left', 'right']
    assert billy.parents[0] is john
    assert billy.parents[1] is mary
    assert billy.siblings[0] is abby

def test_fields():
    tri_data = """---
Triangle[ABC]:
    side1: 2
"""
    abc = load_from_yaml(StringIO(tri_data))
    check_for_undefined_objects()
    assert abc.perimeter() == 4
    assert Triangle.instance('ABC') is abc
    assert Triangle.instance('ABC', side3=4) is abc
    def_ = Triangle.instance('ABC', copy=True, side1=3, side2=2)
    assert def_ is not abc
    assert def_.perimeter() == 6

def test_undefined():
    john_data = """---
Person[John]:
    name: John Smith
    age: 31
    hands:
        - left
        - right
    legs: [left, right]
    spouse: Person[Mary]
    children:
        - Person[Abby]
        - Person[Billy]
"""
    with patch.object(Person, '_lookup', new={}):
        load_from_yaml(StringIO(john_data))
        with pytest.raises(RuntimeError):
            check_for_undefined_objects()
