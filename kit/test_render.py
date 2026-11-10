import unittest
import sys
from pathlib import Path
import tempfile
import json
import xml.etree.ElementTree as ET
import subprocess
import html

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'kit'))
import render as R
import render_hub as H

class TestRenderUnit(unittest.TestCase):
    def test_absolute_url(self):
        self.assertEqual(R.href('index.html'), 'index.html')
        self.assertEqual(R.href('/index.html'), '/index.html')

    def test_text_of(self):
        self.assertEqual(R.text_of({'en': 'Hello', 'zh': 'Nihao'}, 'en'), 'Hello')
        self.assertEqual(R.text_of('Hello', 'en'), 'Hello')
        self.assertEqual(R.text_of('Hello', 'zh'), 'Hello')

    def test_bi(self):
        self.assertEqual(R.bi({'en': 'Hello', 'zh': 'Nihao'}), '<span class="lang-en">Hello</span><span class="lang-zh" lang="zh-Hant">Nihao</span>')
        self.assertEqual(R.bi('Hello'), '<span>Hello</span>')

    def test_inline(self):
        self.assertEqual(R.inline('Hello World'), 'Hello World')
        self.assertEqual(R.inline('Hello <code>Code</code>'), 'Hello <code class="nowrap">Code</code>')

    def test_attr(self):
        self.assertEqual(R.attr('Hello "World"'), 'Hello &quot;World&quot;')

    def test_is_bi(self):
        self.assertTrue(R.is_bi({'en': 'Hello', 'zh': 'Nihao'}))
        self.assertFalse(R.is_bi('Hello'))
        self.assertFalse(R.is_bi({'en': 'Hello'}))

class TestRenderMisc(unittest.TestCase):
    def test_hub_validate(self):
        hub = {'groups': [{'projects': [{'slug': 'test', 'name': 'test', 'repo': 'owner/test', 'mark': '', 'palette': '', 'line': '', 'stack': '', 'status': 'toy'}]}]}
        problems = H.validate(hub)
        self.assertEqual(problems, [])

        hub['groups'][0]['projects'][0]['status'] = 'invalid'
        problems = H.validate(hub)
        self.assertIn('test: status must be one of [\'active\', \'early\', \'notes\', \'paused\', \'stable\', \'toy\', \'utility\']', problems)

    def test_hub_validate_moved(self):
        hub = {'groups': [], 'moved': ['owner/invalid_repo', 'invalid']}
        problems = H.validate(hub)
        self.assertTrue(any('must be owner/name' in p for p in problems))

class TestRenderValidation(unittest.TestCase):
    def test_validate(self):
        page = {
            'repo': 'owner/test', 'slug': 'test', 'name': 'test', 'mark': 'tst',
            'title': {'en': 'title', 'zh': 'title'},
            'description': {'en': 'desc', 'zh': 'desc'},
            'hero': {'eyebrow': {'en': 'a', 'zh': 'b'}, 'headline': {'en': 'a', 'zh': 'b'}, 'lede': {'en': 'a', 'zh': 'b'}, 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'palette': {}, 'visual': {'type': 'stack'}},
            'capabilities': {'title': {'en': 'a', 'zh': 'b'}, 'items': []},
            'status': 'toy', 'facts': []
        }
        problems = R.validate(page)
        self.assertEqual(problems, [])

    def test_validate_problems(self):
        page = {'repo': 'test'}
        problems = R.validate(page)
        self.assertTrue(any('slug' in p for p in problems))

    def test_validate_flows(self):
        page = {'flows': [{'id': 'test', 'heading': {'en': 'a', 'zh': 'b'}, 'intro': {'en': 'a', 'zh': 'b'}, 'caption': {'en': 'a', 'zh': 'b'}, 'spec': {'columns': [[0], [1]], 'core': 0, 'sinks': []}, 'steps': [{'title': {'en': 'a', 'zh': 'b'}, 'note': {'en': 'a', 'zh': 'b'}, 'tone': 'accent', 'icon': 'cloud'}, {'title': {'en': 'a', 'zh': 'b'}, 'note': {'en': 'a', 'zh': 'b'}, 'tone': 'accent', 'icon': 'cloud'}], 'ticks': [{'en': 'a', 'zh': 'b'}], 'connectors': []}]}
        problems = R.validate_flows(page)
        self.assertEqual(problems, [])

    def test_validate_flows_problems(self):
        page = {'flows': 'not a list'}
        problems = R.validate_flows(page)
        self.assertEqual(problems, ["$.flows: must be a list"])

        page = {'flows': [{'id': 'T'}]}
        problems = R.validate_flows(page)
        self.assertTrue(any('id: a lowercase id' in p for p in problems))

class TestRenderComponents(unittest.TestCase):
    def test_anchor(self):
        self.assertEqual(R.anchor({'href': 'https://github.com/foo', 'label': {'en': 'GitHub', 'zh': 'GitHub'}}), '<a href="https://github.com/foo"><span class="lang-en">GitHub</span><span class="lang-zh" lang="zh-Hant">GitHub</span></a>')
        self.assertEqual(R.anchor({'href': 'https://ted-h.com', 'label': 'TED H.'}), '<a href="https://ted-h.com"><span>TED H.</span></a>')
        self.assertEqual(R.anchor({'href': {'en': 'https://en.x.com', 'zh': 'https://zh.x.com'}, 'label': 'X'}), '<a class="lang-en" href="https://en.x.com">X</a><a class="lang-zh" lang="zh-Hant" href="https://zh.x.com">X</a>')

    def test_button(self):
        btn = {'href': 'https://example.com', 'label': {'en': 'Hello', 'zh': 'Nihao'}}
        self.assertEqual(R.button(btn, 'primary'), '<a class="button primary" href="https://example.com"><span class="lang-en">Hello</span><span class="lang-zh" lang="zh-Hant">Nihao</span></a>')

    def test_logo_svg(self):
        svg = R.logo_svg('TST', {'ink': '#000000', 'accent': '#FF0000', 'signal': '#00FF00', 'accent2': '#0000FF', 'canvas': '#FFFFFF', 'paper': '#F0F0F0', 'shade': '#E0E0E0', 'kicker': '#D0D0D0', 'void': '#C0C0C0'}, 48)
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">', svg)
        self.assertIn('TST', svg)

    def test_palette_of(self):
        p1 = R.palette_of({'palette': 'teal'})
        self.assertIn('ink', p1)
        p2 = R.palette_of({'palette': {'ink': '#111', 'accent': '#222', 'signal': '#333', 'accent2': '#444', 'canvas': '#555', 'paper': '#666', 'shade': '#777', 'kicker': '#888', 'void': '#999'}})
        self.assertEqual(p2['ink'], '#111')

class TestRenderUtils(unittest.TestCase):
    def test_rgb_hex_mix(self):
        rgb1 = R._rgb('#FF0000', 'test1')
        self.assertEqual(rgb1, (255, 0, 0))

        rgb2 = R._rgb('#0F0', 'test2')
        self.assertEqual(rgb2, (0, 255, 0))

        hex1 = R._hex((0, 0, 255))
        self.assertEqual(hex1, '#0000ff')

        mix1 = R._mix((255, 0, 0), (0, 255, 0), 0.5)
        self.assertEqual(mix1, '#808000')

    def test_load_private_terms(self):
        terms = R.load_private_terms()
        self.assertTrue(isinstance(terms, list))

    def test_flow_map(self):
        pal = {'ink': '#192C33', 'accent': '#0CA678', 'signal': '#E03131', 'accent2': '#7048E8', 'canvas': '#FFFFFF', 'paper': '#F8F9FA', 'shade': '#E9ECEF', 'kicker': '#868E96', 'void': '#212529'}
        css = R.flow_map(pal)
        self.assertIn('--fd-accent:', css)

class TestRenderPage(unittest.TestCase):
    def test_render_404(self):
        page = {'name': 'test', 'slug': 'test-slug'}
        html = R.render_404(page)
        self.assertIn('<title>test', html)
        self.assertIn('404', html)

    def test_workflow_for(self):
        page = {'default_branch': 'main'}
        yml = R.workflow_for(page)
        self.assertIn('branches: [main]', yml)

        page = {'default_branch': 'main', 'pages_extra': {'paths': ['test_path']}}
        yml = R.workflow_for(page)
        self.assertIn('- "test_path"', yml)

class TestRenderHTML(unittest.TestCase):
    def test_heading(self):
        sec = {'title': {'en': 'Test', 'zh': '測試'}, 'intro': {'en': 'Intro', 'zh': '介紹'}}
        html = R.heading(sec, 'test-class')
        self.assertIn('<div class="section-heading test-class">', html)
        self.assertIn('<h2', html)
        self.assertIn('class="lang-en">Test</h2>', html)
        self.assertIn('<p', html)
        self.assertIn('class="lang-en">Intro</p>', html)

    def test_heading_no_intro(self):
        sec = {'title': {'en': 'Test', 'zh': '測試'}}
        html = R.heading(sec)
        self.assertIn('<div class="section-heading ">', html)
        self.assertNotIn('<p', html)

    def test_panel_top(self):
        visual = {'top': {'en': 'Label', 'zh': '標籤'}, 'badge': {'en': 'Action', 'zh': '行動'}}
        html = R.panel_top(visual)
        self.assertIn('<div class="panel-top">', html)
        self.assertIn('<span class="lang-en">Label</span>', html)
        self.assertIn('<span class="lang-en">Action</span>', html)

    def test_render_flow_section_no_lanes(self):
        flow = {
            'id': 'test', 'heading': {'en': 'test', 'zh': 'test'},
            'intro': {'en': 'test', 'zh': 'test'},
            'spec': {'columns': [[0]], 'core': 0, 'sinks': []},
            'steps': [{'title': {'en': 'test', 'zh': 'test'}, 'note': {'en': 'test', 'zh': 'test'}, 'tone': 'accent', 'icon': 'cloud'}],
            'ticks': [{'en': 'test', 'zh': 'test'}],
            'caption': {'en': 'test', 'zh': 'test'}
        }
        html = R.render_flow_section(flow)
        self.assertIn('id="test"', html)
        self.assertIn('data-fd=', html)

    def test_render_page_basic(self):
        page = {
            'repo': 'owner/test', 'slug': 'test', 'name': 'test', 'mark': 'tst',
            'title': {'en': 'title', 'zh': 'title'},
            'description': {'en': 'desc', 'zh': 'desc'},
            'hero': {'eyebrow': {'en': 'a', 'zh': 'b'}, 'headline': {'en': 'a', 'zh': 'b'}, 'lede': {'en': 'a', 'zh': 'b'}, 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'palette': {'ink': '#111'}, 'visual': {'type': 'stack'}},
            'capabilities': {'title': {'en': 'a', 'zh': 'b'}, 'items': [{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'},{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'},{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'}]},
            'status': {'nav': False, 'title': {'en': 't', 'zh': 't'}}, 'facts': [{'label': {'en': 'a', 'zh': 'b'}, 'value': '1'}],
            'quickstart': {'nav': {'en': 'q', 'zh': 'w'}, 'title': {'en': 'test', 'zh': 'test'}, 'body': [], 'steps': [{'title': {'en': 'test', 'zh': 'test'}, 'code': 'test'}]},
            'flow': {'title': {'en': 't', 'zh': 't'}, 'steps': [{'title': {'en': 't', 'zh': 't'}, 'body': {'en': 't', 'zh': 't'}}]},
            'problem': {'title': {'en': 't', 'zh': 't'}, 'body': {'en': 't', 'zh': 't'}, 'quote': {'en': 't', 'zh': 't'}},
            'stats': [{'label': {'en': 'l', 'zh': 'l'}, 'value': '1'}],
            'showcase': {'title': {'en': 's', 'zh': 's'}, 'intro': {'en': 's', 'zh': 's'}, 'body': ['test', 'test2'], 'shots': [{'src': 'img.png', 'alt': {'en': 'a', 'zh': 'b'}}]},
        }
        assets = {'img.png': 'assets/img.png'}
        html = R.render_page(page, assets)
        self.assertIn('<!doctype html>', html)
        self.assertIn('<title>test', html)
        self.assertIn('id="screens"', html)

    def test_render_visual(self):
        assets = {'test.png': 'assets/test.png'}
        visual_img = {'type': 'image', 'src': 'test.png', 'alt': {'en': 'Test', 'zh': '測試'}}
        html_img = R.render_visual(visual_img, assets)
        self.assertIn('assets/test.png', html_img)

        visual_receipt = {'type': 'receipt', 'top': {'en': 'a', 'zh': 'a'}, 'total': '1', 'rows': [{'label': {'en': 'a', 'zh': 'a'}, 'detail': '1'}]}
        html_receipt = R.render_visual(visual_receipt, assets)
        self.assertIn('check-row', html_receipt)

        visual_terminal = {'type': 'terminal', 'top': {'en': 'a', 'zh': 'a'}, 'lines': [{'text': 'test'}]}
        html_terminal = R.render_visual(visual_terminal, assets)
        self.assertIn('term', html_terminal)

        visual_chat = {'type': 'chat', 'top': {'en': 'a', 'zh': 'a'}, 'messages': [{'role': 'user', 'text': {'en': 'a', 'zh': 'a'}}]}
        html_chat = R.render_visual(visual_chat, assets)
        self.assertIn('bubble bubble-user', html_chat)

        visual_report = {'type': 'report', 'top': {'en': 'a', 'zh': 'a'}, 'title': {'en': 'a', 'zh': 'a'}, 'metrics': [{'label': {'en': 'a', 'zh': 'a'}, 'value': '1'}], 'bars': [{'label': {'en': 'a', 'zh': 'a'}, 'value': 50}]}
        html_report = R.render_visual(visual_report, assets)
        self.assertIn('report', html_report)

    def test_render_flow_section_with_lanes(self):
        flow = {
            'id': 'test2', 'heading': {'en': 'test', 'zh': 'test'},
            'intro': {'en': 'test', 'zh': 'test'},
            'spec': {'columns': [[0], [1]], 'core': 0, 'lanes': [{'title': {'en': 'a', 'zh': 'a'}, 'start': 0, 'end': 1}], 'sinks': []},
            'steps': [{'title': {'en': 'test', 'zh': 'test'}, 'note': {'en': 'test', 'zh': 'test'}, 'tone': 'accent', 'icon': 'cloud'}, {'title': {'en': 'test', 'zh': 'test'}, 'note': {'en': 'test', 'zh': 'test'}, 'tone': 'info', 'icon': 'cloud'}],
            'ticks': [{'en': 'test', 'zh': 'test'}],
            'caption': {'en': 'test', 'zh': 'test'}
        }
        html = R.render_flow_section(flow)
        self.assertIn('data-fd=', html)
        self.assertIn('lanes', html)

    def test_render_404_no_slug(self):
        page = {'name': 'test', 'slug': 'test'}
        html = R.render_404(page)
        self.assertIn('<title>test', html)
        self.assertIn('404', html)

    def test_collect_assets(self):
        page = {
            'hero': {},
            'showcase': {'shots': [{'src': 'test.png'}]}
        }
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            (repo_dir / 'test.png').write_text('dummy')
            assets = R.collect_assets(page, repo_dir)
            self.assertEqual(assets['test.png'], 'assets/test.png')

    def test_collect_assets_not_found(self):
        page = {
            'hero': {},
            'showcase': {'shots': [{'src': 'test.png'}]}
        }
        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            with self.assertRaises(R.PageError):
                R.collect_assets(page, repo_dir)

    def test_workflow_for_no_pages_extra(self):
        page = {'default_branch': 'main'}
        yml = R.workflow_for(page)
        self.assertNotIn('- "test_path"', yml)

    def test_render_default_flow_section(self):
        flows = [
            {'id': 'test1', 'heading': {'en': 'test1', 'zh': 'test1'}, 'intro': {'en': 'test1', 'zh': 'test1'}, 'spec': {'columns': [[0]], 'core': 0, 'sinks': []}, 'steps': [{'title': {'en': 'test1', 'zh': 'test1'}, 'note': {'en': 'test1', 'zh': 'test1'}, 'tone': 'accent', 'icon': 'cloud'}], 'ticks': [{'en': 'test1', 'zh': 'test1'}], 'caption': {'en': 'test1', 'zh': 'test1'}},
            {'id': 'test2', 'heading': {'en': 'test2', 'zh': 'test2'}, 'intro': {'en': 'test2', 'zh': 'test2'}, 'spec': {'columns': [[0]], 'core': 0, 'sinks': []}, 'steps': [{'title': {'en': 'test2', 'zh': 'test2'}, 'note': {'en': 'test2', 'zh': 'test2'}, 'tone': 'accent', 'icon': 'cloud'}], 'ticks': [{'en': 'test2', 'zh': 'test2'}], 'caption': {'en': 'test2', 'zh': 'test2'}}
        ]
        html = R.render_default_flow_section(flows)
        self.assertIn('id="how"', html)
        self.assertIn('id="test1"', html)
        self.assertIn('id="test2"', html)

    def test_place_flows_fallback(self):
        parts = ['<section class="section" id="capabilities"></section>']
        page = {'flows': [
            {'id': 'f1', 'after': 'unknown', 'group': False, 'heading': {'en': 'test1', 'zh': 'test1'}, 'intro': {'en': 'test1', 'zh': 'test1'}, 'spec': {'columns': [[0]], 'core': 0, 'sinks': []}, 'steps': [{'title': {'en': 'test1', 'zh': 'test1'}, 'note': {'en': 'test1', 'zh': 'test1'}, 'tone': 'accent', 'icon': 'cloud'}], 'ticks': [{'en': 'test1', 'zh': 'test1'}], 'caption': {'en': 'test1', 'zh': 'test1'}}
        ]}
        placed = R.place_flows(parts, page)
        self.assertEqual(len(placed), 2)

    def test_place_flows_no_flows(self):
        parts = ['<section class="section" id="capabilities"></section>']
        page = {}
        placed = R.place_flows(parts, page)
        self.assertEqual(placed, parts)

    def test_render_page_sections(self):
        page = {
            'repo': 'owner/test', 'slug': 'test', 'name': 'test', 'mark': 'tst',
            'title': {'en': 'title', 'zh': 'title'},
            'description': {'en': 'desc', 'zh': 'desc'},
            'hero': {'eyebrow': {'en': 'a', 'zh': 'b'}, 'headline': {'en': 'a', 'zh': 'b'}, 'lede': {'en': 'a', 'zh': 'b'}, 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'palette': {'ink': '#111'}, 'visual': {'type': 'stack'}},
            'capabilities': {'title': {'en': 'a', 'zh': 'b'}, 'items': [{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'},{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'},{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'}]},
            'status': {'nav': False, 'title': {'en': 'test', 'zh': 'test'}}, 'facts': [{'label': {'en': 'a', 'zh': 'b'}, 'value': '1'}],
            'quickstart': {'nav': {'en': 'q', 'zh': 'w'}, 'title': {'en': 'test', 'zh': 'test'}, 'body': [], 'steps': [{'title': {'en': 'test', 'zh': 'test'}, 'code': 'test'}]},
            'showcase': {'title': {'en': 's', 'zh': 's'}, 'intro': {'en': 's', 'zh': 's'}, 'body': ['test', 'test2'], 'shots': [{'src': 'img.png', 'alt': {'en': 'a', 'zh': 'b'}}]},
            'architecture': {'title': {'en': 'a', 'zh': 'a'}, 'body': ['test'], 'nodes': [{'name': {'en': 'a', 'zh': 'a'}, 'body': {'en': 'a', 'zh': 'a'}, 'icon': 'cloud', 'lines': [{'en': 'a', 'zh': 'b'}]}]},
            'decisions': {'title': {'en': 'd', 'zh': 'd'}, 'intro': {'en': 'd', 'zh': 'd'}, 'items': [{'title': {'en': 'd', 'zh': 'd'}, 'body': ['test']}]},
            'links': [{'label': 'a', 'href': 'a'}]
        }
        assets = {'img.png': 'assets/img.png'}
        html = R.render_page(page, assets)
        self.assertIn('id="screens"', html)
        self.assertIn('img.png', html)
        self.assertIn('id="architecture"', html)
        self.assertIn('id="decisions"', html)
        self.assertIn('class="footer-links"', html)

    def test_render_page_branches(self):
        page = {
            'repo': 'owner/test', 'slug': 'test', 'name': 'test', 'mark': 'tst',
            'title': {'en': 'title', 'zh': 'title'},
            'description': {'en': 'desc', 'zh': 'desc'},
            'hero': {'eyebrow': {'en': 'a', 'zh': 'b'}, 'headline': {'en': 'a', 'zh': 'b'}, 'lede': {'en': 'a', 'zh': 'b'}, 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'palette': {'ink': '#111'}, 'visual': {'type': 'stack'}, 'secondary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}},
            'capabilities': {'title': {'en': 'a', 'zh': 'b'}, 'items': [{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud'}]},
            'status': {'nav': False, 'title': {'en': 'test', 'zh': 'test'}}, 'facts': [{'label': {'en': 'a', 'zh': 'b'}, 'value': '1'}],
            'quickstart': {'nav': {'en': 'q', 'zh': 'w'}, 'title': {'en': 'test', 'zh': 'test'}, 'body': [], 'steps': [{'title': {'en': 'test', 'zh': 'test'}, 'code': 'test'}], 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'secondary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}}
        }
        html = R.render_page(page, {})
        self.assertIn('button-secondary', html)

    def test_render_page_more_branches(self):
        page = {
            'repo': 'owner/test', 'slug': 'test', 'name': 'test', 'mark': 'tst',
            'title': {'en': 'title', 'zh': 'title'},
            'description': {'en': 'desc', 'zh': 'desc'},
            'hero': {'eyebrow': {'en': 'a', 'zh': 'b'}, 'headline': {'en': 'a', 'zh': 'b'}, 'lede': {'en': 'a', 'zh': 'b'}, 'primary': {'label': {'en': 'a', 'zh': 'b'}, 'href': 'a'}, 'palette': {'ink': '#111'}, 'visual': {'type': 'stack'}},
            'capabilities': {'title': {'en': 'a', 'zh': 'b'}, 'items': [{'title': {'en': 'a', 'zh': 'b'}, 'body': {'en': 'a', 'zh': 'b'}, 'icon': 'cloud', 'tag': 'test'}]},
            'status': {'nav': False, 'title': {'en': 'test', 'zh': 'test'}}, 'facts': [{'label': {'en': 'a', 'zh': 'b'}, 'value': '1'}],
            'architecture': {'title': {'en': 'a', 'zh': 'a'}, 'body': ['test'], 'nodes': [{'name': {'en': 'a', 'zh': 'a'}, 'body': {'en': 'a', 'zh': 'a'}, 'icon': 'cloud', 'lines': [{'en': 'a', 'zh': 'b'}], 'core': True}], 'return': {'en': 'a', 'zh': 'b'}, 'label': {'en': 'a', 'zh': 'b'}, 'principles': {'title': {'en': 'a', 'zh': 'b'}, 'items': [{'en': 'a', 'zh': 'b'}]}},
        }
        html = R.render_page(page, {})
        self.assertIn('tag', html)
        self.assertIn('map-return', html)
        self.assertIn('map-label', html)
        self.assertIn('principles', html)

    def test_cli_execution_errors(self):
        result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

        with tempfile.TemporaryDirectory() as d:
            repo_dir = Path(d)
            site_dir = repo_dir / 'site'
            site_dir.mkdir()
            page = {'repo': 'owner/test'} # Invalid page
            (site_dir / 'page.json').write_text(json.dumps(page))
            result = subprocess.run([sys.executable, str(ROOT / 'kit' / 'render.py'), str(repo_dir)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)

if __name__ == '__main__':
    unittest.main()
