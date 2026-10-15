import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import render_profile as P


class ProfileThemeTests(unittest.TestCase):
    def test_generated_output_is_idempotent_and_preserves_status(self):
        hub = json.loads((Path(__file__).parent.parent / 'hub.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'projects').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (root / name).write_text('## ' + heading + '\n\n' + P.START + '\n' + P.END + '\n')
            first = P.outputs(hub, root)
            for path, text in first.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
                if path.suffix == '.svg':
                    ET.fromstring(text)
            self.assertEqual(first, P.outputs(hub, root))
            self.assertEqual(12, sum(p.suffix == '.svg' for p in first))
            for group in hub['groups']:
                for project in group['projects']:
                    for lang in ('en', 'zh'):
                        row = P.row(project, lang)
                        status = P.H.STATUS[project['status']][lang]
                        self.assertIn(status.upper() if lang == 'en' else status, row)
                        self.assertIn(P.H.project_repo(project), row)

    def test_chrome_preserves_identity_and_existing_production_claim(self):
        original = '## In production.\n\nExisting production description.\n<code>LIVE / MULTI-AI</code>\nhttps://teddashh.github.io/github-profile-summary-cards/teddashh/en/card-medium-light.svg\n'
        rendered = P.profile_chrome(original, 'en')
        self.assertIn('Existing production description.', rendered)
        self.assertIn('https://ted-h-com.github.io/github-profile-summary-cards/teddashh/en/', rendered)
        self.assertEqual(rendered, P.profile_chrome(rendered, 'en'))
        self.assertIn('1A7F37', rendered)


if __name__ == '__main__':
    unittest.main()
