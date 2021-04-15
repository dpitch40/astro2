from astro.configurable import Configurable

class WaveCondition(Configurable):
    defaults = {'delay': 0.0}

    def __init__(self, key):
        super().__init__(key)
        self.triggered = False

    def ready(self, now, elapsed, current_formations):
        if not self.triggered and self._ready(now, elapsed, current_formations):
            self.triggered = True
            self.triggered_time = now
        if self.triggered:
            return now - self.triggered_time >= self.delay
        return False

    def _ready(self, now, elapsed, current_formations):
        raise NotImplementedError

class Timer(WaveCondition):
    required_fields = ('time',)

    def _ready(self, now, elapsed, current_formations):
        last_deployment = max(f.deployed for f in current_formations)
        return now - last_deployment > self.time

class PercentOfLastWave(WaveCondition):
    required_fields = ('percent',)

    def _ready(self, now, elapsed, current_formations):
        last_wave_i = max(f.wave_i for f in current_formations)
        last_wave = [f for f in current_formations if f.wave_i == last_wave_i]
        total_ships = sum([f.num_ships for f in last_wave])
        total_ships_remaining = sum([f.ships_remaining for f in last_wave])
        return total_ships_remaining / total_ships <= self.percent

class LastWaveDefeated(PercentOfLastWave):
    required_fields = ()

    def initialize(self):
        self.percent = 0.0
        super().initialize()

class PercentOfAllWaves(WaveCondition):
    required_fields = ('percent',)

    def _ready(self, now, elapsed, current_formations):
        total_ships = sum([f.num_ships for f in current_formations])
        total_ships_remaining = sum([f.ships_remaining for f in current_formations])
        return total_ships_remaining / total_ships <= self.percent

class AllWavesDefeated(PercentOfAllWaves):
    required_fields = ()

    def initialize(self):
        self.percent = 0.0
        super().initialize()

