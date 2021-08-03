import time
import heapq

from astro.configurable import Configurable

class Effect(Configurable):
    def apply(self, ship):
        pass

    def stop(self, ship):
        pass

class TimedEffect(Effect):
    required_fields = ('duration',)

    def apply(self, ship):
        heapq.heappush(ship.timed_effects, (time.time() + self.duration, self))

class MindControl(TimedEffect):
    def apply(self, ship):
        super().apply(ship)
        ship.become_friendly()

    def stop(self, ship):
        ship.become_enemy()
