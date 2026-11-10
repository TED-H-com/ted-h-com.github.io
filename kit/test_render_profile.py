import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))
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


class TestRenderProfileUnit(unittest.TestCase):
    def test_directory(self):
        hub = {'groups': [{'id': 'test', 'title': {'en': 'Test', 'zh': 'Test'}, 'projects': [{'slug': 'test', 'name': 'test', 'status': 'toy', 'line': {'en': 'test', 'zh': 'test'}}]}]}
        md = P.directory(hub)
        self.assertIn('Projects', md)
        self.assertIn('teddashh/test', md)

    def test_splice(self):
        original = 'hello\n' + P.START + '\nold\n' + P.END + '\nworld'
        new_block = 'new'
        spliced = P.splice(original, new_block, Path('test.md'))
        self.assertEqual(spliced, 'hello\nnew\nworld')

        with self.assertRaises(P.H.R.PageError):
            P.splice('hello world', new_block, Path('test.md'))

    def test_cli_execution_errors(self):
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_profile.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_profile.py'), str(repo_dir)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)

    def test_cli_execution_check_only(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'projects').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (repo_dir / name).write_text('## ' + heading + '\n\n' + P.START + '\n' + P.END + '\n')
            result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_profile.py'), str(repo_dir), '--check'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('out of date', result.stdout)

    def test_cli_execution_success(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'projects').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (repo_dir / name).write_text('## ' + heading + '\n\n' + P.START + '\n' + P.END + '\n')

            subprocess.run(['python3', 'kit/render_profile.py', str(repo_dir)], capture_output=True, text=True)

            result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render_profile.py'), str(repo_dir), '--check'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('profile: ok', result.stdout)

    def test_section_svg(self):
        svg = P.section_svg('test title', 'test subtitle')
        self.assertIn('test title', svg)
        self.assertIn('test subtitle', svg)

    def test_outputs_error(self):
        hub = {'groups': [{'id': 'test', 'kicker': {'en': 'a', 'zh': 'b'}, 'summary': {'en': 'a', 'zh': 'b'}, 'title': {'en': 'Test', 'zh': 'Test'}, 'projects': [{'slug': 'test', 'name': 'test', 'status': 'toy', 'line': {'en': 'test \u2014 test', 'zh': 'test'}, 'stack': 'test'}]}]}
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'projects').mkdir()
            (repo_dir / 'assets').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (repo_dir / name).write_text('## ' + heading + '\n\n' + P.START + '\n\n' + P.END + '\n')

            with self.assertRaises(Exception):
                P.outputs(hub, repo_dir)

    def test_outputs_pointer(self):
        hub = {'groups': [{'id': 'test', 'kicker': {'en': 'a', 'zh': 'b'}, 'summary': {'en': 'a', 'zh': 'b'}, 'title': {'en': 'Test', 'zh': 'Test'}, 'projects': [{'slug': 'test', 'name': 'test', 'status': 'toy', 'line': {'en': 'test', 'zh': 'test'}, 'stack': 'test'}]}]}
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'projects').mkdir()
            (repo_dir / 'assets').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (repo_dir / name).write_text('## ' + heading + '\n\n' + P.START + '\n\n' + P.END + '\n')
            (repo_dir / 'projects' / 'test.md').write_text('dummy')
            files = P.outputs(hub, repo_dir)
            self.assertIn('https://teddashh.github.io/test/', files[repo_dir / 'projects' / 'test.md'])

    def test_outputs_pointer_missing(self):
        hub = {'groups': [{'id': 'test', 'kicker': {'en': 'a', 'zh': 'b'}, 'summary': {'en': 'a', 'zh': 'b'}, 'title': {'en': 'Test', 'zh': 'Test'}, 'projects': [{'slug': 'test', 'name': 'test', 'status': 'toy', 'line': {'en': 'test', 'zh': 'test'}, 'stack': 'test'}]}]}
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'projects').mkdir()
            (repo_dir / 'assets').mkdir()
            for name, heading in [('README.md', 'In production.'), ('README.zh-TW.md', '正在線上運作。')]:
                (repo_dir / name).write_text('## ' + heading + '\n\n' + P.START + '\n\n' + P.END + '\n')
            (repo_dir / 'projects' / 'unknown.md').write_text('dummy')
            with self.assertRaises(P.H.R.PageError):
                P.outputs(hub, repo_dir)

if __name__ == '__main__':
    unittest.main()
