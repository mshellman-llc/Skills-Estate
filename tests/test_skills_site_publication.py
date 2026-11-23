import base64
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import urllib.error

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('site_release_builder', 'artifacts/skills-site/build_release.py')
publisher = module('site_release_publisher', 'artifacts/skills-site/publish.py')


class SiteReleaseTests(unittest.TestCase):
    def test_complete_build_is_deterministic_and_public_content_is_projected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            one = builder.build(path / 'one')
            two = builder.build(path / 'two')
            self.assertEqual(one, two)
            manifest, files = publisher.read_release(path / 'one', one['sourceCommit'])
            data = {}
            for audience in ['private', 'public']:
                html = files[audience + '.html'].decode()
                data[audience] = json.loads(re.search(r'<script id="estate-data" type="application/json">(.*?)</script>', html, re.S)[1])
                self.assertIn((ROOT / 'artifacts/skills-site/page.css').read_text().strip(), html)
                self.assertEqual(one['sourceCommit'], data[audience]['sourceCommit'])
            self.assertEqual('workspace', data['private']['target'])
            self.assertEqual('portfolio', data['public']['target'])
            self.assertTrue(data['public']['publicMap'])
            publication = json.loads(files['catalog.json'])['publication']['targets']['portfolio']['skills']
            visible = {s['id'] for s in data['public']['skills']}
            self.assertEqual({id for id, value in publication.items() if value['visible']}, visible)
            for skill in data['public']['skills']:
                self.assertFalse(skill.get('src'))
                self.assertFalse(skill.get('setup'))
                self.assertTrue(set(skill.get('uses', [])) <= visible)
            for workflow in data['public']['workflows']:
                self.assertTrue({s['skill'] for s in workflow['steps']} <= visible)
            (path / 'one/public.html').write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                publisher.read_release(path / 'one', one['sourceCommit'])

    def test_publisher_is_atomic_idempotent_and_refuses_a_rollback(self):
        source, previous = 'a' * 40, 'b' * 40
        manifest = {'format': 1, 'sourceCommit': source, 'files': {}}
        calls = []
        def api(method, url, body=None):
            calls.append((method, url, body))
            if '/git/ref/heads/' in url:
                return {'object': {'sha': previous}}
            if '/contents/release.json' in url:
                return {'content': base64.b64encode(json.dumps({'sourceCommit': 'c' * 40}).encode()).decode()}
            if '/compare/' in url:
                return {'status': 'ahead'}
            return {'sha': 'd' * 40}
        result = publisher.publish(api, manifest, {'private.html': b'private', 'public.html': b'public', 'release.json': b'{}'})
        self.assertTrue(result['published'])
        writes = [call for call in calls if call[0] != 'GET']
        self.assertEqual('PATCH', writes[-1][0])
        self.assertTrue(writes[-1][1].endswith('/git/refs/heads/site-publication'))
        self.assertFalse(writes[-1][2]['force'])
        self.assertEqual([previous], next(body['parents'] for method, url, body in writes if url.endswith('/git/commits')))
        for status in ['behind', 'diverged']:
            def refuse(method, url, body=None):
                if '/compare/' in url:
                    return {'status': status}
                self.assertEqual('GET', method)
                return api(method, url, body)
            if status == 'behind':
                self.assertFalse(publisher.publish(refuse, manifest, {})['published'])
            else:
                with self.assertRaisesRegex(ValueError, 'diverged'):
                    publisher.publish(refuse, manifest, {})
        def repeat(method, url, body=None):
            self.assertEqual('GET', method)
            return {'object': {'sha': previous}} if '/git/ref/' in url else {'content': base64.b64encode(json.dumps(manifest).encode()).decode()}
        self.assertFalse(publisher.publish(repeat, manifest, {})['published'])
        with self.assertRaisesRegex(ValueError, 'different'):
            publisher.publish(repeat, {**manifest, 'files': {'changed': {}}}, {})

    def test_publisher_creates_a_new_branch_without_touching_main(self):
        writes = []
        def api(method, url, body=None):
            if method == 'GET':
                raise urllib.error.HTTPError(url, 404, 'absent', {}, None)
            writes.append((url, body))
            return {'sha': 'a' * 40}
        publisher.publish(api, {'sourceCommit': 'b' * 40}, {'release.json': b'{}'})
        self.assertEqual('refs/heads/site-publication', writes[-1][1]['ref'])
        self.assertFalse(any(url.endswith('/heads/main') for url, _ in writes))


if __name__ == '__main__':
    unittest.main()
