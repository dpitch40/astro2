from astro.configurable import Configurable

class Campaign(Configurable):
    required_fields = ('name', 'levels')

    def __init__(self, key):
        Configurable.__init__(self, key)
        self.level_i = 0

    def complete(self):
        return self.level_i >= len(self.levels)

    def reset(self):
        self.level_i = 0

    def won_level(self):
        self.level_i += 1

    def current_level(self):
        return self.levels[self.level_i]

    def serialize(self):
        return {'key': self.key,
                'level_i': self.level_i}

    @classmethod
    def deserialize(cls, obj):
        instance = cls.instance(obj['key'])
        instance.level_i = obj['level_i']
        return instance
