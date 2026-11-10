"""Local owner choices and isolated website previews. Never shipped in public exports."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import tempfile
from urllib.parse import unquote
import zipfile

import publication


class Conflict(ValueError):
    pass


class OwnerStore:
    def __init__(self, output, settings=None):
        self.output = Path(output).resolve()
        self.settings = Path(settings).resolve() if settings else (publication.CONFIG if publication.CONFIG.exists() else self.output.parent / 'visibility.json')
        repository = publication.HERE.parents[1]
        self.state = repository / '.local/website-publication' if (repository / '.git').exists() else self.output.parent / '.skills-estate-owner'
        self.exports = self.state / 'exports'
        self.history = self.state / 'history'

    def current(self):
        if self.settings.exists():return publication.load(self.settings)
        return {'format': 1, 'targets': {target: {kind: {} for kind in publication.KINDS} for target in publication.TARGETS}}

    def data(self):
        return json.loads(self.output.with_suffix('.json').read_text())

    def read(self):
        settings = self.current()
        return {'settings': settings, 'revision': publication.revision(settings), 'inventory': publication.inventory(self.data()), 'settingsFile': str(self.settings)}

    def save(self, settings, expected):
        publication.validate(settings)
        current = self.current()
        if expected != publication.revision(current):raise Conflict('Choices changed in another window. Download your draft before reloading the current choices.')
        self.history.mkdir(parents=True, exist_ok=True)
        stamp = secrets.token_hex(12)
        backup = self.history / (stamp + '.json')
        backup.write_text(json.dumps(current, indent=2) + '\n')
        self.settings.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix='.' + self.settings.name, dir=self.settings.parent)
        try:
            with os.fdopen(descriptor, 'w') as stream:
                json.dump(settings, stream, indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
            os.replace(name, self.settings)
        finally:
            if os.path.exists(name):os.unlink(name)
        (self.history / 'previous.json').write_text(json.dumps({'file': backup.name, 'sha256': hashlib.sha256(backup.read_bytes()).hexdigest()}))
        return {'revision': publication.revision(settings), 'message': 'Choices saved in this checkout. Export or commit them when ready.'}

    def restore(self, expected):
        pointer = self.history / 'previous.json'
        if not pointer.exists():raise ValueError('There is no previous save to restore')
        info = json.loads(pointer.read_text())
        path = self.history / info['file']
        if path.parent != self.history or not path.is_file() or path.is_symlink():raise ValueError('Invalid saved choices')
        if hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256']:raise ValueError('Previous choices changed on disk')
        settings = json.loads(path.read_text())
        result = self.save(settings, expected);result['settings'] = settings
        return result

    def preview(self, settings, target):
        publication.validate(settings)
        data = self.data()
        self.exports.mkdir(parents=True, exist_ok=True)
        key = secrets.token_hex(8)
        output = self.exports / key
        packages = self.output.parent / 'downloads' / data['baseCommit']
        if not (packages / 'manifest.json').is_file():
            packages = publication.HERE.parents[1] / 'dist'
            release = packages / 'release.json'
            if not release.is_file() or json.loads(release.read_text()).get('source_commit') != data['baseCommit']:packages = None
        manifest, omitted = publication.export(data, settings, target, output, packages)
        archive = self.exports / (key + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted(output.rglob('*')):
                if path.is_file():z.write(path, str(path.relative_to(output)))
        return {'preview': '/exports/' + key + '/index.html', 'archive': '/exports/' + key + '.zip', 'counts': {k: manifest[k] for k in ('skills', 'workflows', 'plugins')}, 'taskDownloadsIncluded': manifest['taskDownloadsIncluded'], 'blockedWorkflows': omitted}

    def file(self, request):
        if '?' in request or '#' in request:return None
        path = unquote(request.removeprefix('/exports/'))
        parts = Path(path).parts
        if not parts or parts[0] in ('.', '..') or any(p in ('.', '..') for p in parts):return None
        root = self.exports.resolve(); candidate = (root / path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file() or candidate.is_symlink():return None
        return candidate
