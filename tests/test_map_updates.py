"""Verify GitHub snapshot selection, safe replacement, and localhost update boundaries."""
import contextlib
import hashlib
import http.client
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('map_viewer',ROOT/'artifacts/skills-map/viewer.py')
viewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(viewer)
COMMIT='a'*40

def snapshot(commit=COMMIT,status='github'):
    source='---\nname: sample\ndescription: Sample workflow.\n---\n# Sample\n'
    data={'repository':viewer.REPOSITORY,'baseCommit':commit,'counts':{'total':1},'skills':[{'id':'sample','status':status,'markdown':source,'sourceSha256':hashlib.sha256(source.encode()).hexdigest()}]}
    text='<html><script type="application/json" id="estate-data">'+json.dumps(data)+'</script><script id="map-viewer-config" type="application/json">__MAP_VIEWER_CONFIG__</script></html>'
    return data,text

def archive(data,text,extra=None):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        z.writestr('index.json',json.dumps(data));z.writestr('index.html',text)
        if extra:z.writestr(*extra)
    return out.getvalue()

def api_for(payload,run_commit=COMMIT,latest=COMMIT,expired=False):
    def api(path,raw=False):
        if path=='commits/main':return {'sha':latest}
        if path.startswith('actions/runs?'):return {'workflow_runs':[{'id':3,'head_sha':run_commit,'head_branch':'main','event':'push','path':'.github/workflows/verify.yml','conclusion':'success'}]}
        if path.startswith('actions/runs/3/artifacts'):return {'artifacts':[{'id':4,'name':'skills-estate-map','expired':expired}]}
        if path=='actions/artifacts/4/zip':return payload
        raise AssertionError(path)
    return api

class MapUpdateTests(unittest.TestCase):
    def test_current_main_build_replaces_both_files(self):
        data,text=snapshot()
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'map.html';output.write_text('old')
            result=viewer.refresh(output,api_for(archive(data,text)))
            self.assertEqual(result['commit'],COMMIT);self.assertEqual(output.read_text(),text)
            self.assertEqual(json.loads(output.with_suffix('.json').read_text()),data)

    def test_pending_or_expired_build_preserves_current_map(self):
        data,text=snapshot()
        for api in [api_for(archive(data,text),run_commit='b'*40),api_for(archive(data,text),expired=True)]:
            with self.subTest(api=api),tempfile.TemporaryDirectory() as tmp:
                output=Path(tmp)/'map.html';output.write_text('keep this map')
                with self.assertRaises(ValueError):viewer.refresh(output,api)
                self.assertEqual(output.read_text(),'keep this map')
                self.assertFalse(output.with_suffix('.json').exists())

    def test_wrong_source_mismatched_data_and_unpublished_skills_are_rejected(self):
        cases=[]
        data,text=snapshot(commit='b'*40);cases.append(archive(data,text))
        data,text=snapshot(status='local-revision');cases.append(archive(data,text))
        data,text=snapshot();data['counts']['total']=2;cases.append(archive(data,text))
        data,text=snapshot();cases.append(archive(data,text,('../escape.txt','bad')))
        data,text=snapshot();cases.append(archive(data,text,('nested/index.html','duplicate')))
        for payload in cases:
            with self.subTest(size=len(payload)),self.assertRaises(ValueError):viewer.validate_download(payload,COMMIT)

    def test_head_advancing_during_download_preserves_current_map(self):
        data,text=snapshot();api=api_for(archive(data,text));calls=0
        def changing(path,raw=False):
            nonlocal calls
            if path=='commits/main':
                calls+=1
                if calls>1:return {'sha':'b'*40}
            return api(path,raw)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'map.html';output.write_text('old')
            with self.assertRaises(ValueError):viewer.refresh(output,changing)
            self.assertEqual(output.read_text(),'old')

    def test_server_requires_same_origin_nonce_and_no_request_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'map.html';output.write_text(snapshot()[1])
            server=viewer.MapServer(output);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                def request(method,path,headers=None,body=None):
                    c=http.client.HTTPConnection('127.0.0.1',server.server_port)
                    c.request(method,path,body=body,headers=headers or {});r=c.getresponse();status=r.status;content=r.read();c.close();return status,content
                self.assertEqual(request('GET','/')[0],200)
                self.assertIn(server.token.encode(),request('GET','/')[1])
                self.assertEqual(request('GET','/../../etc/passwd')[0],404)
                self.assertEqual(request('GET','/',{'Host':'evil.example'})[0],403)
                self.assertEqual(request('POST','/api/update')[0],403)
                headers={'Origin':server.origin,'X-Map-CSRF':server.token}
                self.assertEqual(request('POST','/api/update',{**headers,'Origin':'https://evil.example'})[0],403)
                self.assertEqual(request('POST','/api/update',headers,body='{}')[0],400)
                with patch.object(viewer,'refresh',return_value={'skills':1}) as refresh:
                    self.assertEqual(request('POST','/api/update',headers)[0],200);refresh.assert_called_once_with(output)
                with patch.object(viewer,'refresh',side_effect=ValueError('Still building')):
                    self.assertEqual(request('POST','/api/update',headers)[0],502)
                    self.assertIn(b'Still building',request('GET','/api/status')[1])
            finally:server.shutdown();server.server_close();thread.join()
