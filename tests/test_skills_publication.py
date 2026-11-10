"""Exercise publication selection, durable owner choices and portable boundaries."""
import copy
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import threading
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / 'artifacts/skills-map'
sys.path.insert(0, str(MAP))
import publication
from owner import OwnerStore, Conflict
sys.path.insert(0, str(ROOT / 'tools'))
from test_capabilities import integration
import viewer


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = [{
            'id': key, 'title': key.title(), 'family': 0, 'description': key,
            'status': 'github', 'markdown': '# ' + key, 'html': '<h2>' + key + '</h2>',
            'mentions': [{'name': other, 'context': other}], 'profile': {'bundles': [other], 'calls': [], 'dependsOn': [], 'usedBy': []},
            'downloadPackages': [key], 'catalogRole': {'kind': 'task', 'tasks': [key], 'modes': []},
            'examples': [], 'headings': [], 'resources': [], 'excerptHtml': '', 'taskPackages': [{'name': key, 'mode': None}],
        } for key, other in [('one', 'two'), ('two', 'one')]]
        self.data = {'schemaVersion': 1, 'skills': self.skills, 'families': [{'id': 'general', 'title': 'General', 'description': 'General work'}], 'baseCommit': 'a'*40, 'repository': 'fixture', 'generatedAt': '2026-11-10T00:00:00Z', 'counts': {'total': 2}, 'pluginInventory': [{'id': 'estate-test', 'description': 'Fixture plugin'}]}
        self.routes = [{'id': 'both', 'title': 'Both skills', 'audience': 'General', 'desc': 'Use both', 'inputs': 'Sources', 'prompt': 'Review sources', 'outcome': 'A result', 'note': 'Check inputs', 'steps': [{'skill': 'one', 'why': 'First'}, {'skill': 'two', 'why': 'Second'}]}]
        self.bundles = {'estate-test': {'description': 'Fixture plugin'}}
        self.settings = {'format': 1, 'targets': {t: {k: {} for k in publication.KINDS} for t in publication.TARGETS}}
        for target in publication.TARGETS:
            for kind, ids in [('skills', ['one', 'two']), ('workflows', ['both']), ('plugins', ['estate-test'])]:
                for key in ids:self.settings['targets'][target][kind][key] = {'visible': True, 'download': True, 'featured': False, 'order': 1000}

    def test_targets_are_independent_and_new_items_are_hidden(self):
        self.settings['targets']['portfolio']['skills']['two']['visible'] = False
        estate, blocked = publication.project(self.data, self.settings, 'estate', self.routes, self.bundles)
        portfolio, blocked = publication.project(self.data, self.settings, 'portfolio', self.routes, self.bundles)
        self.assertEqual([s['id'] for s in estate['skills']], ['one', 'two'])
        self.assertEqual([s['id'] for s in portfolio['skills']], ['one'])
        self.assertEqual(portfolio['skills'][0]['mentions'], [])
        self.assertEqual(portfolio['skills'][0]['profile']['bundles'], [])
        self.assertEqual(portfolio['workflows'], [])
        self.assertEqual(blocked, [{'id': 'both', 'missing': ['two']}])
        self.assertFalse(publication.choice(self.settings, 'estate', 'skills', 'new')['visible'])
        self.assertEqual(len(self.data['skills']), 2)

    def test_disabling_downloads_preserves_visible_content(self):
        self.settings['targets']['estate']['skills']['one']['download'] = False
        self.settings['targets']['estate']['plugins']['estate-test']['download'] = False
        result, _ = publication.project(self.data, self.settings, 'estate', self.routes, self.bundles)
        self.assertEqual(len(result['skills']), 2)
        self.assertEqual(result['skills'][0]['downloadPackages'], [])
        self.assertFalse(result['skills'][0]['downloadAllowed'])
        self.assertEqual(result['plugins'][0]['url'], '')
        self.assertNotIn('pluginInventory', result)

    def test_settings_reject_invalid_shapes_and_values(self):
        for field, value in [('visible', 'yes'), ('order', -1), ('order', True)]:
            settings = copy.deepcopy(self.settings);settings['targets']['estate']['skills']['one'][field] = value
            with self.assertRaises(ValueError):publication.validate(settings)
        settings = copy.deepcopy(self.settings);settings['targets']['estate']['skills']['../../outside'] = settings['targets']['estate']['skills'].pop('one')
        with self.assertRaises(ValueError):publication.validate(settings)

    def test_save_restore_and_concurrent_edit_protection(self):
        settings = self.root / 'choices.json';settings.write_text(json.dumps(self.settings))
        store = OwnerStore(self.root / 'map.html', settings);store.state = self.root / 'owner';store.history = store.state / 'history';store.exports = store.state / 'exports'
        expected = publication.revision(self.settings)
        changed = copy.deepcopy(self.settings);changed['targets']['estate']['skills']['one']['visible'] = False
        saved = store.save(changed, expected)
        self.assertFalse(publication.load(settings)['targets']['estate']['skills']['one']['visible'])
        with self.assertRaises(Conflict):store.save(self.settings, expected)
        self.assertEqual(publication.revision(store.current()), saved['revision'])
        restored = store.restore(saved['revision'])
        self.assertTrue(restored['settings']['targets']['estate']['skills']['one']['visible'])
        self.assertEqual(restored['revision'], expected)
        self.assertTrue(list(store.history.glob('*.json')))

    def test_export_contains_only_selected_records_and_no_manager(self):
        data = json.loads((MAP / 'index.json').read_text());settings = publication.load()
        # Export a single portfolio skill while leaving the estate selection intact.
        settings = copy.deepcopy(settings)
        for row in settings['targets']['portfolio']['skills'].values():row['visible'] = False
        skill = data['skills'][0]['id'];settings['targets']['portfolio']['skills'][skill]['visible'] = True
        output = self.root / 'public'
        manifest, _ = publication.export(data, settings, 'portfolio', output)
        public = json.loads((output / 'catalog.json').read_text())
        self.assertEqual([s['id'] for s in public['skills']], [skill])
        self.assertFalse((output / 'manage.html').exists())
        self.assertFalse((output / 'visibility.json').exists())
        self.assertNotIn('targets', public['publication'])
        self.assertIn('export function mountSkillsEstate', (output / 'skills-estate.js').read_text())
        self.assertIn('skills-estate-explorer', (output / 'skills-estate.js').read_text())
        self.assertIn('assets/inter-license.txt', manifest['files'])
        css = (output / 'explorer.css').read_text()
        self.assertIn('.inline-detail .dialog-body{', css)
        self.assertNotIn('.dialog-.estate-root', css)
        self.assertIn('integration-example.html', manifest['files'])
        self.assertIn('index.html', manifest['files'])
        self.assertFalse(manifest['taskDownloadsIncluded'])
        self.assertNotIn('__ESTATE_', (output / 'index.html').read_text())
        with self.assertRaises(ValueError):publication.export(data, settings, 'portfolio', output)

    def test_download_archive_requires_exact_commit_and_hash(self):
        data = json.loads((MAP / 'index.json').read_text());settings = publication.load()
        packages = self.root / 'packages';packages.mkdir()
        manifest = {'commit': 'b'*40, 'packages': {}}
        (packages / 'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'match the catalog'):
            publication.export(data, settings, 'estate', self.root / 'bad-commit', packages)
        manifest['commit'] = data['baseCommit']
        for name in {n for s in data['skills'] for n in s['downloadPackages']}:
            path = packages / (name + '.zip')
            with zipfile.ZipFile(path, 'w') as z:z.writestr('SKILL.md', '# Fixture')
            manifest['packages'][name] = {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        (packages / 'manifest.json').write_text(json.dumps(manifest))
        result, _ = publication.export(data, settings, 'estate', self.root / 'valid', packages)
        self.assertTrue(result['taskDownloadsIncluded'])
        first = next(iter(manifest['packages']));(packages / (first + '.zip')).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            publication.export(data, settings, 'estate', self.root / 'bad-hash', packages)

    @integration('loopback')
    def test_owner_http_boundaries_save_conflict_and_filtered_preview(self):
        output = self.root / 'index.html';output.write_text((MAP / 'index.html').read_text())
        output.with_suffix('.json').write_text((MAP / 'index.json').read_text())
        settings = publication.load();path = self.root / 'choices.json';path.write_text(json.dumps(settings))
        server = viewer.MapServer(output, settings=path)
        server.owner.state = self.root / 'state';server.owner.history = server.owner.state / 'history';server.owner.exports = server.owner.state / 'exports'
        thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
        self.addCleanup(thread.join);self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        headers = {'Origin': server.origin, 'X-Map-CSRF': server.token}
        def request(method, route, body=None, extra=None):
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
            connection.request(method, route, body=None if body is None else json.dumps(body), headers=extra if extra is not None else headers)
            response = connection.getresponse();content = response.read();status = response.status;connection.close()
            return status, content
        self.assertEqual(request('GET', '/api/publication', extra={})[0], 403)
        self.assertEqual(request('GET', '/manage', extra={'Host':'other.example'})[0], 403)
        self.assertEqual(request('POST', '/api/publication/save', {}, {**headers,'Origin':'https://other.example'})[0], 403)
        self.assertEqual(request('POST', '/api/publication/save', [])[0], 400)
        status, content = request('GET', '/api/publication');self.assertEqual(status, 200)
        initial = json.loads(content);settings['targets']['estate']['skills']['assess-offering-fit']['visible'] = False
        body = {'settings':settings,'expectedRevision':initial['revision']}
        self.assertEqual(request('POST', '/api/publication/save', body)[0], 200)
        self.assertEqual(request('POST', '/api/publication/save', body)[0], 409)
        status, content = request('POST', '/api/publication/preview', {'settings': settings, 'target':'estate'})
        self.assertEqual(status, 200);preview = json.loads(content)
        self.assertEqual(preview['counts']['skills'], 90);self.assertTrue(preview['blockedWorkflows'])
        status, content = request('GET', preview['preview'].replace('index.html','catalog.json'))
        self.assertEqual(status, 200)
        self.assertNotIn('assess-offering-fit', {s['id'] for s in json.loads(content)['skills']})
        self.assertEqual(request('GET', preview['preview'].replace('index.html','manage.html'))[0],404)

    def test_export_path_cannot_escape_owner_directory(self):
        store = OwnerStore(self.root / 'map.html', self.root / 'choices.json');store.exports = self.root / 'exports';store.exports.mkdir()
        (self.root / 'private.txt').write_text('Private')
        self.assertIsNone(store.file('/exports/../private.txt'))
        self.assertIsNone(store.file('/exports/%2e%2e/private.txt'))
        (store.exports / 'link.txt').symlink_to(self.root / 'private.txt')
        self.assertIsNone(store.file('/exports/link.txt'))

    def test_every_workflow_has_valid_steps_and_useful_context(self):
        routes = json.loads((MAP / 'workflows.json').read_text())
        data = json.loads((MAP / 'index.json').read_text());ids = {s['id'] for s in data['skills']}
        self.assertGreaterEqual(len(routes), 18)
        self.assertGreaterEqual(len({r['audience'] for r in routes}), 8)
        self.assertEqual(len({r['id'] for r in routes}), len(routes))
        for route in routes:
            for key in ('inputs', 'prompt', 'outcome', 'note'):self.assertGreater(len(route[key]), 60, (route['id'], key))
            self.assertTrue(route['steps'])
            for step in route['steps']:
                self.assertIn(step['skill'], ids)
                self.assertGreater(len(step['why']), 45)

    @integration('browser')
    def test_owner_and_embedded_component_in_browser(self):
        output = self.root / 'index.html';output.write_text((MAP / 'index.html').read_text())
        output.with_suffix('.json').write_text((MAP / 'index.json').read_text())
        choices = self.root / 'visibility.json';choices.write_text(json.dumps(publication.load()))
        server = viewer.MapServer(output, settings=choices)
        server.owner.state = self.root / 'state';server.owner.history = server.owner.state / 'history';server.owner.exports = server.owner.state / 'exports'
        thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
        try:
            result = subprocess.run([os.environ.get('ESTATE_NODE','node'),str(MAP / 'verify_portable.cjs'),server.origin],cwd=ROOT,capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        finally:server.shutdown();server.server_close();thread.join()


if __name__ == '__main__':unittest.main()
