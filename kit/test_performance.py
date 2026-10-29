import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent

class PerformanceHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))

class TestPerformance(unittest.TestCase):
    def test_bundle_size_limits(self):
        """Check that CSS and JS bundles are within acceptable limits."""
        site_dir = ROOT / 'site'

        MAX_CSS = 50 * 1024  # 50 KB
        MAX_JS = 100 * 1024   # 100 KB

        for f in site_dir.rglob('*.css'):
            self.assertLess(f.stat().st_size, MAX_CSS, f"CSS bundle {f.name} exceeds {MAX_CSS} bytes")

        for f in site_dir.rglob('*.js'):
            self.assertLess(f.stat().st_size, MAX_JS, f"JS bundle {f.name} exceeds {MAX_JS} bytes")

    def test_lazy_loading(self):
        """Check that images use lazy loading (except for logos/heroes)."""
        site_dir = ROOT / 'site'
        index_file = site_dir / 'index.html'

        parser = PerformanceHTMLParser()
        parser.feed(index_file.read_text(encoding='utf-8'))

        lazy_count = 0
        for img in parser.images:
            src = img.get('src', '')
            if src.startswith('tiles/'):
                self.assertEqual(img.get('loading'), 'lazy', f"Project tile {src} should be lazy loaded")
                lazy_count += 1

        self.assertGreater(lazy_count, 0, "No lazy loaded images found")

    def test_static_asset_compression(self):
        """Check that SVG assets are optimized/compressed (no large files)."""
        site_dir = ROOT / 'site'

        for f in site_dir.rglob('*.svg'):
            # Even complex optimized SVGs should be relatively small
            self.assertLess(f.stat().st_size, 5 * 1024, f"SVG asset {f.name} is too large, may need compression")

            content = f.read_text(encoding='utf-8')
            # Check for common uncompressed SVG artifacts like comments or unnecessary editor metadata
            self.assertNotIn('<!--', content, f"SVG asset {f.name} contains uncompressed comments")
            self.assertNotIn('inkscape:', content, f"SVG asset {f.name} contains Inkscape metadata")
            self.assertNotIn('sodipodi:', content, f"SVG asset {f.name} contains Sodipodi metadata")

if __name__ == '__main__':
    unittest.main()
