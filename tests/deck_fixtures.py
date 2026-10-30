"""Portable deck fixtures shared without importing another test case."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class DeckFixture:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.pkg = self.base / 'deck-builder'
        assemble(ROOT, 'deck-builder', self.pkg, [])
        self.data = json.loads((self.pkg / 'examples/reconciliation.json').read_text())
        self.counter = 0

    def run_build(self, data=None, extra=(), output='deck.html'):
        self.counter += 1
        source = self.base / f'input-{self.counter}.json'
        source.write_text(json.dumps(self.data if data is None else data))
        dest = self.base / output
        proc = subprocess.run([sys.executable, str(self.pkg / 'scripts/build_html.py'),
                               str(source), str(dest), *extra], cwd=self.base,
                              capture_output=True, text=True)
        (self.base / f'result-{self.counter}.json').write_text(json.dumps({
            'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}, indent=2))
        return proc, dest
