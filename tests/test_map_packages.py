import hashlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('map_packages',ROOT/'artifacts/skills-map/packages.py')
packages=importlib.util.module_from_spec(spec);spec.loader.exec_module(packages)

def archive(files):
    target=io.BytesIO()
    with zipfile.ZipFile(target,'w') as z:
        for name,value in files.items():z.writestr(name,value)
    return target.getvalue()

class PackageDownloadTests(unittest.TestCase):
    def fixture(self):
        task=archive({'task/SKILL.md':'Entrypoint','task/_runtime/helper/WORKFLOW.md':'Complete helper','task/references/guide.md':'Reference','task/scripts/run.py':'print(1)'})
        release={'source_sha256':'a'*64,'packages':{'task':{'file':'task.zip','sha256':hashlib.sha256(task).hexdigest()}}}
        data={'baseCommit':'b'*40,'skills':[{'downloadPackages':['task']}]}
        return task,release,data

    def test_complete_packages_and_dependencies_survive(self):
        task,release,data=self.fixture()
        payloads,manifest=packages.validate(archive({'task.zip':task,'release.json':json.dumps(release)}),data)
        self.assertEqual(payloads['task.zip'],task)
        self.assertEqual(manifest['commit'],data['baseCommit'])
        with zipfile.ZipFile(io.BytesIO(payloads['task.zip'])) as z:
            self.assertIn('task/_runtime/helper/WORKFLOW.md',z.namelist())

    def test_changed_zip_is_rejected(self):
        task,release,data=self.fixture()
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            packages.validate(archive({'task.zip':task+b'changed','release.json':json.dumps(release)}),data)

    def test_escaping_inner_archive_is_rejected(self):
        _,release,data=self.fixture();task=archive({'task/SKILL.md':'entry','../outside':'bad'})
        release['packages']['task']['sha256']=hashlib.sha256(task).hexdigest()
        with self.assertRaisesRegex(ValueError,'Unsafe'):
            packages.validate(archive({'task.zip':task,'release.json':json.dumps(release)}),data)

    def test_mismatched_inventory_is_rejected(self):
        task,release,data=self.fixture();data['skills'][0]['downloadPackages'].append('missing')
        with self.assertRaisesRegex(ValueError,'inventories differ'):
            packages.validate(archive({'task.zip':task,'release.json':json.dumps(release)}),data)

if __name__=='__main__':unittest.main()
