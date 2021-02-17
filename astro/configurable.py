"""Defines a superclass for objects that are instantiated from YAML configs.

"""

import os.path
import re

from yaml import safe_load

# Regex for identifying references to Configurables
configurable_re = re.compile(r"^(\w+)\[(\w+)\]$")
# Mapping allowign lookup of Configurable subclasses by name
_configurable_class_lookup = dict()
_undefined_objects = set()

class _ConfigurableMeta(type):
    """Metaclass for Configurable and its subclasses that initializes them in the lookup systems.
    """
    def __new__(cls, name, bases, namespace):
        # Instantiate the new class
        result = type.__new__(cls, name, bases, dict(namespace))
        # Add it to the Configurable (sub)class lookup dict
        _configurable_class_lookup[name] = result 
        # Initialize its instance lookup dict
        result._lookup = dict()
        return result

class Configurable(metaclass=_ConfigurableMeta):
    defaults = dict()
    required_fields = ()

    """Superclass for objects meant to be instantiated from YAML and looked up by key.
    """
    def __init__(self, key):
        self.key = key
        self._initialized = False

    def _setup(self, _config):
        """Initializes this object using a dictionary loaded from a config file.

        Args:
            config (dict): A dictionary whose keys will become attributes of this object.
        """
        config = self.defaults.copy()
        config.update(_config)
        for k, v in config.items():
            setattr(self, k, load_from_obj(v))

    def check_required_fields(self):
        """Checks that this object is "ready for primetime", i.e. that all of its
           required fields have been filled in.

        Raises:
            RuntimeError if any required fields are missing.
        """
        # Check for required fields
        missing_fields = [f for f in self.required_fields if not hasattr(self, f)]
        if missing_fields:
            raise RuntimeError(f'{self.__class__.__name__} is missing fields:\n' +
                '\n'.join(missing_fields))

    def initialize(self):
        """Final initialization performed on an instance of a configurable just before
           it is returned.

           Subclasses can override this to perform any final setup that relies on all
           expected fields being set.
        """
        self.check_required_fields()
        self._initialized = True

    def copy(self, **overrides):
        """Creates and returns a new instance of this instance's class.

        The new instance

        Args:
            overrides (dict): Any attributes to change for the copy. They default to be the same
                as those of the called object.

        Returns:
            A new instance of the called instance's class.
        """
        _, base_config = self._lookup[self.key]
        config = base_config.copy()
        config.update(overrides)
        copied = self.__class__(self.key)
        copied._setup(config)
        return copied

    @classmethod
    def _define(cls, key, config):
        """Defines the base instance of a Configurable and adds it to the instance lookup.

        Args:
            key (str): A unique key that identifies this instance.
            config (dict): A dictionary that will be used to configure the object.
        """
        if key in cls._lookup:
            # Should only be called once, to add an instance to the instance lookup
            raise RuntimeError(f"Base instance of {key} already exists")

        # Initialize and setup the base instance
        inst = cls(key)
        inst._setup(config)
        # Add it and its config dict to the instabce lookup
        cls._lookup[key] = (inst, config)
        return inst

    @classmethod
    def _instance(cls, key, copy=False, **overrides):
        if key not in cls._lookup:
            raise RuntimeError(f"No base instance of {key} created")
        base_instance, _ = cls._lookup[key]
        if copy:
            inst = base_instance.copy(**overrides)
        else:
            inst = base_instance
        return inst

    @classmethod
    def instance(cls, key, copy=False, **overrides):
        """Returns an instance of the Configurable identified by a key.

        Args:
            key (str): A unique key that identifies the desired instance.
            copy (bool): If False, return the base instance. If True, return a new instance.
            overrides (dict): Has no effect if copy is False. If copy is True, updates the
                returned instance with its contents.

        Returns:
            A new instance of the class.
        """
        inst = cls._instance(key, copy=copy, **overrides)
        if not inst._initialized:
            inst.initialize()
        return inst

def _check_for_configurable(s):
    """Checks if a string identifies an instance of a Configurable.

    Args:
        s (str): A string.
    
    Returns:
        A 2-tuple. (None, None) if s does not identify an instance of a Configurable.
        Otherwise, returns the instance's class and key.
    """
    m = configurable_re.match(s)
    if m:
        name, key = m.groups()
        if name in _configurable_class_lookup:
            return _configurable_class_lookup[name], key
    return None, None

def load_from_yaml(path_or_fobj):
    """Loads and returns a Configurable from YAML.

    Args:
        path_or_fobj: A file path or file-like object.

    Returns:
        A Configurable instance.
    """
    if isinstance(path_or_fobj, str) and os.path.isfile(path_or_fobj):
        with open(path_or_fobj, 'r') as fobj:
            data = safe_load(fobj)
    else:
        data = safe_load(path_or_fobj)
    return load_from_obj(data)

def load_from_obj(obj):
    """Recursive helper function for loading Configurables.

    Initializes or dereferences Configurables in obj, passes other values through.
    Works recursively on data structures.
    """
    if isinstance(obj, dict):
        if len(obj) == 1:
            k, v = next(iter(obj.items()))
            class_, key = _check_for_configurable(k)
            if class_:
                if key in class_._lookup:
                    # Update an already-defined instance
                    obj = class_._instance(key)
                    class_._lookup[key] = (obj, v)
                    obj._setup(v)
                    obj.initialize()
                    _undefined_objects.discard((class_, key))
                    return obj
                else:
                    # Define the instance
                    obj = class_._define(key, v)
                    # Lazy initialization
                    obj.initialize()
                    return obj
        # Apply recursively
        return {k: load_from_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Apply recursively
        return [load_from_obj(v) for v in obj]
    elif isinstance(obj, str):
        class_, key = _check_for_configurable(obj)
        if class_:
            if key in class_._lookup:
                # Dereference the instance
                obj = class_._instance(key)
            else:
                # Define the instance with an empty config, to be setup later
                obj = class_._define(key, {})
                _undefined_objects.add((class_, key))

    # Default to passing objects through
    return obj

def check_for_undefined_objects():
    if _undefined_objects:
        lines = '\n'.join([f'\t- {class_.__name__}[{key}]' for class_, key in sorted(_undefined_objects)])
        raise RuntimeError(f"The following referenced Configurables were not defined:\n{lines}")
