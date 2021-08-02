from astro.configurable import Configurable

class Effect(Configurable):
    def apply(self, ship):
        raise NotImplementedError

    def stop(self, ship):
        raise NotImplementedError

class MindControl(Effect):
    required_fields = ('duration')

    def apply(self, ship):
        ship.become_friendly()
        ship.timed_effects.append([self, self.duration])

    def stop(self, ship):
        ship.become_enemy()
