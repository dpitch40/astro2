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

class AddVFX(TimedEffect):
    required_fields = TimedEffect.required_fields + ('vfx',)

    def apply(self, ship):
        super().apply(ship)
        self.vfx_inst = self.vfx.copy()
        self.vfx_inst.place(ship.screen, ship)

    def stop(self, ship):
        self.vfx_inst.destroy()

class MindControl(TimedEffect):
    def apply(self, ship):
        super().apply(ship)
        ship.become_friendly()

    def stop(self, ship):
        ship.become_enemy()

class BehaviorChange(TimedEffect):
    defaults = {'move_behavior': None,
                'fire_behavior': None}

    def apply(self, ship):
        super().apply(ship)
        if self.move_behavior is not None:
            self.old_move_behavior = ship.move_behavior
            ship.move_behavior = self.move_behavior.copy()
            ship.move_behavior.init_ship(ship)
        if self.fire_behavior is not None:
            self.old_fire_behavior = ship.fire_behavior
            ship.fire_behavior = self.fire_behavior.copy()
            ship.fire_behavior.init_ship(ship)

    def stop(self, ship):
        if self.move_behavior is not None:
            ship.move_behavior = self.old_move_behavior
        if self.fire_behavior is not None:
            ship.fire_behavior = self.old_fire_behavior
