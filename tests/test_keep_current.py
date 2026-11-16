"""keep_current.py reads each tool's plugin list and finds what lags behind main."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import keep_current  # noqa: E402

CODEX_LIST = """Marketplace `skills-estate`
/Users/x/.codex/.tmp/marketplaces/skills-estate/.claude-plugin/marketplace.json
estate-career@skills-estate       installed, disabled  0.4.30   /x/plugins/estate-career
estate-writing@skills-estate      installed, enabled   0.4.35   /x/plugins/estate-writing
estate-salesforce@skills-estate   not installed                 /x/plugins/estate-salesforce
hercules-real-estate@openai-curated-remote   not installed   1.0.0   plugin_asdk_app_1
"""


class KeepCurrent(unittest.TestCase):
    def test_reads_claude_code_plugins_and_skips_other_marketplaces(self):
        text = json.dumps([
            {'id': 'estate-writing@skills-estate', 'version': '0.4.22', 'scope': 'user'},
            {'id': 'estate-career@skills-estate', 'version': '0.4.35'},
            {'id': 'figma@claude-plugins-official', 'version': '2.0.0', 'scope': 'user'},
        ])
        found = keep_current.claude_plugins(text)
        self.assertEqual(found, [('estate-writing@skills-estate', '0.4.22', 'user'),
                                 ('estate-career@skills-estate', '0.4.35', 'user')])
        self.assertEqual(keep_current.lagging(found, '0.4.35'), [('estate-writing@skills-estate', '0.4.22', 'user')])

    def test_bad_claude_output_reads_as_nothing_installed(self):
        self.assertEqual(keep_current.claude_plugins('not json'), [])

    def test_reads_installed_codex_plugins_only(self):
        found = keep_current.codex_plugins(CODEX_LIST)
        self.assertEqual(found, [('estate-career@skills-estate', '0.4.30'), ('estate-writing@skills-estate', '0.4.35')])
        self.assertEqual(keep_current.lagging(found, '0.4.35'), [('estate-career@skills-estate', '0.4.30')])

    def test_hooks_commit_reads_the_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            hooks = Path(tmp)
            self.assertIsNone(keep_current.hooks_commit(hooks))
            (hooks / 'MANIFEST.json').write_text(json.dumps({'commit': 'abc123', 'files': {}}))
            self.assertEqual(keep_current.hooks_commit(hooks), 'abc123')

    def test_a_dry_run_on_current_hooks_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            hooks = Path(tmp)
            (hooks / 'MANIFEST.json').write_text(json.dumps({'commit': 'abc123'}))
            report = {'actions': [], 'errors': []}
            keep_current.keep_hooks(Path(tmp), 'abc123', report, dry=True, hooks=hooks)
            self.assertEqual(report['actions'], [])
            self.assertFalse(report['hooks']['behind'])
            keep_current.keep_hooks(Path(tmp), 'def456', report, dry=True, hooks=hooks)
            self.assertTrue(report['hooks']['behind'])
            self.assertEqual(report['actions'], [])


if __name__ == '__main__':
    unittest.main()
