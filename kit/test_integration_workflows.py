import unittest
import sys
from pathlib import Path
import tempfile
import json
import subprocess

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))
import render_hub as H

class TestIntegrationWorkflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = json.loads((ROOT / 'hub.json').read_text(encoding='utf-8'))
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.site_dir = Path(cls.temp_dir.name)
        (cls.site_dir / 'hub.json').write_text(json.dumps(cls.hub))

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_cli_execution_check_only(self):
        # tests executing main function with --check flag via command line args
        result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_hub.py'), str(self.site_dir), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('hub.json: ok (check only)', result.stdout)

    def test_cli_execution_render(self):
        result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_hub.py'), str(self.site_dir)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.site_dir / 'site' / 'index.html').exists())
        self.assertTrue((self.site_dir / 'site' / 'robots.txt').exists())
        self.assertIn('rendered', result.stdout)

if __name__ == '__main__':
    unittest.main()
