from unittest.mock import patch

from astro.timekeeper import Timekeeper

def test_tick():
    times = list()

    class TestTimekeeper(Timekeeper):
        def tick(self, now, elapsed):
            times.append((now, elapsed))

    tk = TestTimekeeper()
    with patch('time.time', side_effect=[0.0, 0.5, 0.75, 1.5]):
        tk._tick()
        tk._tick()
        tk._tick()
        tk._tick()

    assert times == [(0.5, 0.5), (0.75, 0.25), (1.5, 0.75)]
