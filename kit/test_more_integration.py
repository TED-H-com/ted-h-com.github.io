import unittest
import sys
from pathlib import Path
import tempfile
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))
import render_hub as H

class TestMoreIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = json.loads((ROOT / 'hub.json').read_text(encoding='utf-8'))
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.site_dir = Path(cls.temp_dir.name)
        (cls.site_dir / 'hub.json').write_text(json.dumps(cls.hub))
        H.main(['render_hub.py', str(cls.site_dir)])
        cls.site_path = cls.site_dir / 'site'

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_robots_txt(self):
        robots_file = self.site_path / 'robots.txt'
        self.assertTrue(robots_file.exists())
        content = robots_file.read_text(encoding='utf-8')
        self.assertIn('User-agent: *', content)
        self.assertIn('Allow: /', content)
        self.assertIn('Sitemap:', content)

    def test_nojekyll(self):
        nojekyll_file = self.site_path / '.nojekyll'
        self.assertTrue(nojekyll_file.exists())

    def test_404_page(self):
        not_found_file = self.site_path / '404.html'
        self.assertTrue(not_found_file.exists())
        content = not_found_file.read_text(encoding='utf-8')
        self.assertIn('404', content)

if __name__ == '__main__':
    unittest.main()
