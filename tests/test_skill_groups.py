"""Keep every source workflow in one map/GitHub group and preserve packaged modes."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import browse
from catalog import entries

class SkillGroupTests(unittest.TestCase):
    def test_all_modules_are_in_exactly_one_group_and_documents_are_current(self):
        groups=browse.load_groups(ROOT)
        modules={p.parent.name for p in ROOT.glob('skills/*/SKILL.md')}
        assigned=[n for g in groups for n in g['skills'] if n in modules]
        self.assertEqual(set(assigned),modules);self.assertEqual(len(assigned),len(modules));self.assertEqual(browse.write_pages(ROOT,check=True),[])
        data=json.loads((ROOT/'artifacts/skills-map/index.json').read_text())
        self.assertEqual([g['id'] for g in groups],[g['id'] for g in data['families']])
        for skill in data['skills']:self.assertIn(skill['id'],groups[skill['family']]['skills'])

    def test_duplicate_missing_and_unknown_group_members_are_rejected(self):
        data=json.loads((ROOT/'config/skill-groups.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir();(root/'skills/sample').mkdir(parents=True);(root/'skills/sample/SKILL.md').write_text('sample')
            config=root/'config/skill-groups.json'
            for members in [['sample','sample'],['other'],[]]:
                fixture={'format':1,'groups':[{'id':'test','title':'Test','description':'Test tasks.','skills':members}]}
                config.write_text(json.dumps(fixture))
                with self.subTest(members=members),self.assertRaises(ValueError):browse.load_groups(root)

    def test_task_packages_cover_primary_and_cross_group_modes(self):
        groups=browse.load_groups(ROOT);catalog=entries(ROOT)
        assigned=[n for g in groups for n,item in catalog.items() if item['source'] in g['skills']]
        self.assertEqual(set(assigned),set(catalog));self.assertEqual(len(assigned),len(catalog))
        scope=next(g for g in groups if g['id']=='scope-and-proposals')
        scope_page=(ROOT/'browse/scope-and-proposals/README.md').read_text()
        for name in ['deck-builder','system-design']:self.assertIn('`'+name+'`',scope_page)
        for g in groups:
            page=(ROOT/f"browse/{g['id']}/README.md").read_text()
            for n,item in catalog.items():
                if item['source'] not in g['skills'] and not set(item.get('modes',{}).values()) & set(g['skills']):continue
                self.assertIn('`'+n+'`',page)
                for module in item.get('modes',{}).values():self.assertIn('/'+module+'/SKILL.md)',page)
