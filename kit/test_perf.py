import unittest
import timeit
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))

import render as R
import render_hub as H

class TestPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = json.loads((ROOT / 'hub.json').read_text(encoding='utf-8'))

    def test_rendering_speed(self):
        # We enforce a baseline rendering performance. The core rendering functions
        # were optimized to use explicit stacks rather than recursion and optimized regex/escape calls.
        def validate_run():
            H.validate(self.hub)

        def render_run():
            H.render_hub(self.hub)

        # These are conservative thresholds, enough to fail if O(n^2) behavior is introduced
        # or if the recursion/slow regex implementations are reverted.
        time_validate = timeit.timeit(validate_run, number=20)
        time_render = timeit.timeit(render_run, number=20)

        self.assertLess(time_validate, 2.0, f"H.validate is too slow: {time_validate}s for 20 iterations")
        self.assertLess(time_render, 2.0, f"H.render_hub is too slow: {time_render}s for 20 iterations")

if __name__ == '__main__':
    unittest.main()
