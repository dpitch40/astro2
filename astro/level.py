from astro.configurable import Configurable
from astro.timekeeper import Timekeeper

class Level(Configurable, Timekeeper):
    required_keys = ('waves',)

    def __init__(self, key):
        Configurable.__init__(self, key)
        Timekeeper.__init__(self)
        self.wave_i = 0

    def initialize(self):
        self.num_waves = len(self.waves)
        self.current_formations = list()

    def deploy_wave(self):
        wave_info = self.waves[self.wave_i]
        for formation in wave_info['formations']:
            self.current_formations.append(formation)
            formation.deploy()
            formation.wave_i = self.wave_i

        self.wave_i += 1

    def complete_level(self):
        # TODO
        print('Congratulations, you won!')
        raise SystemExit

    def done(self):
        return self.wave_i >= self.num_waves and sum(f.ships_remaining for f in
            self.current_formations) == 0

    def next_wave_ready(self, now, elapsed):
        if self.wave_i >= len(self.waves):
            return False # No more waves!

        wave_info = self.waves[self.wave_i]
        return wave_info['condition'].ready(now, elapsed, self.current_formations)

    def start(self):
        self.deploy_wave()

    def tick(self, now, elapsed):
        if self.done():
            self.complete_level()

        if self.next_wave_ready(now, elapsed):
            self.deploy_wave()

        delete_indices = list()
        for i, formation in enumerate(self.current_formations):
            formation.update()
            if formation.ships_remaining == 0:
                delete_indices.append(i)

        # Trim empty formations
        for i in delete_indices[::-1]:
            del self.current_formations[i]
