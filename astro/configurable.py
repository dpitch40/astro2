"""Defines a superclass for objects that are defined and instantiated from YAML configs.

The basic syntax for config files is as follows. They are loaded as YAML, but certain strings
and dictionary values will be interpreted as definitions of or references to Configurable objects.
The syntax for a Configurable definition is a dictionary mapping one or more strings of the format

<Name of a Configurable subclass>[<A unique key which may be used to refer to this instance>]:
    configitem1: ...
    configitem2: ...

The instance will have the subdictionary applied to its own dictionary, i.e. all keys in the subdict
will become attributes of the defined instance.

There are two ways to refer to a previously defined instance with a string value. First:

<Name of a Configurable subclass>[<key>]

This is simply the dictionary key from the definition syntax as a string. This will directly
reference the previously defined instance. To use a copy of the instance instead of the original, use
parentheses instead of square backets:

<Name of a Configurable subclass>(<key>)

Additionally, when referencing a copy, you may override any config values you wish using the same syntax you
did when defining the instance, only again with parentheses instead of square brackets.

<Name of a Configurable subclass>(<Key>):
    overridden_configitem1: ...

See the unit test module for usage examples.
"""

import os.path
import re

from yaml import safe_load

# Regex for identifying references to Configurables
configurable_re = re.compile(r"^(\w+)\[(\w*)\]$")
configurable_copy_re = re.compile(r"^(\w+)\((\w*)\)$")
# Mapping allowign lookup of Configurable subclasses by name
_configurable_class_lookup = dict()
_undefined_objects = set()

class ConfigurableMeta(type):
    """Metaclass for Configurable and its subclasses that initializes them in the lookup systems.
    """
    def __init__(self, *args, **kwargs):
        type.__init__(self, *args, **kwargs)
        _configurable_class_lookup[self.__name__] = self
        self._lookup = dict()

    @property
    def fields(self):
        # Prevent inheriting fields
        if '_fields' in self.__dict__:
            return self._fields
        else:
            raise AttributeError(f'fields not defined for {self.__name__}')

    @fields.setter
    def fields(self, value):
        self._fields = value

class Configurable(metaclass=ConfigurableMeta):
    # Fields that must be specified in the configuration
    required_fields = ()
    # Default values for fields that may optionally be specified in the configuration
    defaults = dict()
    # Other attributes that will be copied to new instances as if they were fields
    extra_copy_fields = list()

    """Superclass for objects meant to be instantiated from YAML and looked up by key.
    """
    def __init__(self, key):
        self.key = key
        self.initialized = False

    @property
    def class_name(self):
        return self.__class__.__name__

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

    def _initialize(self):
        if not self.initialized:
            self.initialize()
            self.initialized = True

    def initialize(self):
        """Final initialization performed on an instance of a configurable just before
           it is returned.

           Subclasses can override this to perform any final setup that relies on all
           expected fields being set.
        """
        pass

    @classmethod
    def _set_fields(cls, base_config):
        if not hasattr(cls, 'fields'):
            cls.fields = set(cls.defaults.keys()) | set(cls.required_fields) | set(cls.extra_copy_fields)
            cls.fields = sorted(cls.fields)
            for k in base_config.keys():
                if k not in cls.fields:
                    cls.fields.append(k)

    @property
    def fields(self):
        return self.__class__.fields

    def copy_value(self, value):
        if isinstance(value, dict):
            return {k: self.copy_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.copy_value(v) for v in value]
        elif isinstance(value, Configurable):
            return value.copy()
        else:
            return value

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
        config.update({f: self.copy_value(getattr(self, f)) for f in self.fields if hasattr(self, f)})
        config.update(overrides)
        copied = self.__class__(self.key)
        copied._setup(config)
        copied._initialize()

        return copied

    @classmethod
    def define(cls, key, config):
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
        inst.check_required_fields()
        inst._initialize()
        # Add it and its config dict to the instabce lookup
        cls._lookup[key] = (inst, config)
        cls._set_fields(config)
        return inst

    @classmethod
    def anonymous_instance(cls, config):
        cls._set_fields(config)
        inst = cls(None)
        inst._setup(config)
        inst.check_required_fields()
        inst._initialize()
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

        if key not in cls._lookup:
            raise RuntimeError(f"No base instance of {cls.__name__}[{key}] created")

        base_instance, _ = cls._lookup[key]
        if copy:
            inst = base_instance.copy(**overrides)
        else:
            inst = base_instance
        return inst

    def __repr__(self):
        if hasattr(self, 'name'):
            return f'{self.class_name}({self.name})'
        else:
            return f'{self.class_name}({self.key}): {super().__repr__()}'

    def serialize(self):
        d = dict()
        for f in self.fields:
            if hasattr(self, f):
                value = getattr(self, f)
                d[f] = self._serialize(value)
        return d

    @staticmethod
    def _serialize(value):
        if isinstance(value, Configurable):
            return {f'{value.class_name}({value.key})': value.serialize()}
        elif isinstance(value, dict):
            return {Configurable._serialize(k): Configurable._serialize(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [Configurable._serialize(v) for v in value]
        else:
            return value

def _check_for_configurable(s):
    """Checks if a string identifies an instance of a Configurable.

    Args:
        s (str): A string.
    
    Returns:
        A 3-tuple. (None, None, None) if s does not identify an instance of a Configurable.
        Otherwise, returns the instance's class and key and whether a copy was requested.
    """
    m = configurable_re.match(s)
    m2 = configurable_copy_re.match(s)
    name = None
    if m:
        name, key = m.groups()
        copy = False
    elif m2:
        name, key = m2.groups()
        copy = True

    if name in _configurable_class_lookup:
        return _configurable_class_lookup[name], key, copy
    return None, None, None

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
    try:
        return load_from_obj(data)
    except Exception as e:
        print('Error occurred when loading', path_or_fobj)
        raise

def load_from_obj(obj, dict_key=None):
    """Recursive helper function for loading Configurables.

    Initializes or dereferences Configurables in obj, passes other values through.
    Works recursively on data structures.
    """
    if isinstance(obj, dict):
        if dict_key:
            class_, key, copy = _check_for_configurable(dict_key)
            if class_:
                return load_configurable(class_, key, copy, d=obj)

        # Apply recursively
        result = dict()
        for k, v in obj.items():
            loaded = load_from_obj(v, dict_key=k)
            if isinstance(loaded, Configurable) and loaded.key:
                result[loaded.key] = loaded
            else:
                result[k] = loaded
        if len(result) > 1:
            return result
        else:
            return next(iter(result.values()))
    elif isinstance(obj, list):
        # Apply recursively
        return [load_from_obj(v) for v in obj]
    elif isinstance(obj, str):
        class_, key, copy = _check_for_configurable(obj)
        if class_:
            # Dereference the instance
            return load_configurable(class_, key, copy)

    return obj

def load_configurable(class_, key, copy, d=None):
    """Interprets a reference to a Configurable instance.

    If copy is False and a config dictionary is passed, defines the instance.
    if copy is False and no config dictionary is passed, references a previously defined instance.
    Otherwise, returns a copy, using the config dictionary (if any) to override base values.
    """
    if key == '':
        return class_.anonymous_instance(d if d else {})
    elif copy:
        return class_.instance(key, copy, **(d if d else {}))
    else:
        if d is not None:
            # Define the base instance
            return class_.define(key, d)
        else:
            # Return the base instacce
            return class_.instance(key, copy)
