import unittest
import sys
from pathlib import Path
import tempfile
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))
import render_hub as H

class TestE2EIntegration(unittest.TestCase):
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

    def test_basic_rendering(self):
        index_file = self.site_path / 'index.html'
        self.assertTrue(index_file.exists())

        # Check generated sitemap
        sitemap = self.site_path / 'sitemap.xml'
        self.assertTrue(sitemap.exists())

        tree = ET.parse(sitemap)
        root = tree.getroot()
        urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        self.assertGreater(len(urls), 0)

if __name__ == '__main__':
    unittest.main()
