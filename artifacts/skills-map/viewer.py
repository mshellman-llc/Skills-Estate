#!/usr/bin/env python3
"""Open the map locally and refresh it from the GitHub main build."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import webbrowser
import zipfile
import mimetypes

import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from owner import OwnerStore, Conflict

REPOSITORY='mshellman-llc/Skills-Estate'
MAX_ARCHIVE=96*1024*1024
MAX_FILE=32*1024*1024

def github(path, raw=False):
    executable=shutil.which('gh')
    if not executable:
        candidate=Path.home()/'.local/bin/gh'
        if candidate.is_file():executable=str(candidate)
    if not executable:raise ValueError('GitHub CLI is required. Install gh and sign in to GitHub, then reopen the map.')
    result=subprocess.run([executable,'api','--hostname','github.com','repos/'+REPOSITORY+'/'+path],capture_output=True,timeout=90)
    if result.returncode:
        raise ValueError('GitHub could not provide the map. Check your gh login, repository access, and connection.')
    if len(result.stdout)>MAX_ARCHIVE:raise ValueError('GitHub download exceeds the map size limit')
    return result.stdout if raw else json.loads(result.stdout)

def validate_download(raw, commit):
    if not re.fullmatch(r'[0-9a-f]{40}',commit):raise ValueError('Invalid GitHub commit')
    if len(raw)>MAX_ARCHIVE:raise ValueError('Map archive is too large')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        found={}
        for info in archive.infolist():
            name=PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in info.filename:
                raise ValueError('Unsafe map archive path')
            if info.file_size>MAX_FILE or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('Unsafe map archive entry')
            if name.name in {'index.html','index.json'}:
                if name.name in found:raise ValueError('Duplicate map file')
                found[name.name]=archive.read(info)
        if set(found)!={'index.html','index.json'}:raise ValueError('The build does not contain a complete map')
    data=json.loads(found['index.json'])
    html=found['index.html'].decode('utf-8')
    match=re.search(r'<script type="application/json" id="estate-data">(.*?)</script>',html,re.S)
    if not match or json.loads(match[1])!=data:raise ValueError('HTML and map data do not match')
    if data.get('baseCommit')!=commit or data.get('repository')!=REPOSITORY:
        raise ValueError('The map build does not match current GitHub main. Wait for its workflow to finish and retry.')
    skills=data.get('skills',[])
    if not skills or len({s['id'] for s in skills})!=len(skills) or data.get('counts',{}).get('total')!=len(skills):
        raise ValueError('Invalid map inventory')
    if any(s.get('status')!='github' for s in skills):raise ValueError('Refusing a map with unpublished skill changes')
    for skill in skills:
        if hashlib.sha256(skill['markdown'].encode()).hexdigest()!=skill['sourceSha256']:
            raise ValueError('Skill source hash does not match')
    return found,data

def atomic_write(path, raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temp=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        with os.fdopen(descriptor,'wb') as stream:stream.write(raw)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def refresh(output, api=github):
    output=Path(output)
    if output.is_symlink() or output.with_suffix('.json').is_symlink():raise ValueError('Choose a regular map output path')
    commit=api('commits/main')['sha']
    runs=api('actions/runs?branch=main&status=completed&per_page=30')['workflow_runs']
    eligible=[r for r in runs if r.get('head_sha')==commit and r.get('conclusion')=='success'
              and r.get('head_branch')=='main' and r.get('event') in {'push','workflow_dispatch'}
              and r.get('path')=='.github/workflows/verify.yml']
    eligible.sort(key=lambda r:r['id'],reverse=True)
    if not eligible:raise ValueError('The latest GitHub map is still building or needs a passing workflow. Your current map is kept.')
    artifacts=api(f"actions/runs/{int(eligible[0]['id'])}/artifacts?per_page=100")['artifacts']
    maps=[a for a in artifacts if a.get('name')=='skills-estate-map' and not a.get('expired')]
    if not maps:raise ValueError('The map download is unavailable or expired. Run the GitHub workflow again.')
    artifact=max(maps,key=lambda a:a['id'])
    payload,data=validate_download(api(f"actions/artifacts/{int(artifact['id'])}/zip",raw=True),commit)
    if api('commits/main')['sha']!=commit:raise ValueError('GitHub changed during the download. Update again to get the latest map.')
    atomic_write(output.with_suffix('.json'),payload['index.json'])
    atomic_write(output,payload['index.html'])
    return {'commit':commit,'skills':len(data['skills']),'message':'Up to date with GitHub main'}

class MapServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, output, port=0, settings=None):
        self.output=Path(output);self.token=secrets.token_urlsafe(32);self.lock=threading.Lock();self.last_error=None
        self.owner=OwnerStore(output,settings)
        super().__init__(('127.0.0.1',port),MapHandler)
        self.origin=f'http://127.0.0.1:{self.server_port}'

class MapHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def respond(self,status,body,kind='application/json'):
        if not isinstance(body,bytes):body=json.dumps(body).encode()
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(body)
    def allowed_host(self):return self.headers.get('Host')==self.server.origin[len('http://'):]
    def do_GET(self):
        if not self.allowed_host():self.respond(403,{'error':'Unexpected host'});return
        if self.path=='/':
            if not self.server.output.is_file():self.respond(404,{'error':'No map has been downloaded yet'});return
            text=self.server.output.read_text()
            config=json.dumps({'csrf':self.server.token,'origin':self.server.origin,'manage':True}).replace('<','\\u003c')
            text=text.replace('__MAP_VIEWER_CONFIG__',config)
            self.respond(200,text.encode(),'text/html; charset=utf-8')
        elif self.path=='/manage':
            text=Path(__file__).with_name('manage.html').read_text().replace('__OWNER_CONFIG__',json.dumps({'csrf':self.server.token}).replace('<','\\u003c'))
            self.respond(200,text.encode(),'text/html; charset=utf-8')
        elif self.path=='/api/publication':
            if not secrets.compare_digest(self.headers.get('X-Map-CSRF',''),self.server.token):self.respond(403,{'error':'Open the local content manager first'});return
            try:self.respond(200,self.server.owner.read())
            except (ValueError,OSError,KeyError) as error:self.respond(400,{'error':str(error)})
        elif self.path.startswith('/exports/'):
            file=self.server.owner.file(self.path)
            if not file:self.respond(404,{'error':'Unknown export file'});return
            self.respond(200,file.read_bytes(),mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
        elif self.path=='/api/status':self.respond(200,{'error':self.server.last_error})
        elif self.path=='/favicon.ico':self.respond(204,b'','image/x-icon')
        else:self.respond(404,{'error':'Unknown map route'})
    def do_POST(self):
        if not self.allowed_host() or self.headers.get('Origin')!=self.server.origin or not secrets.compare_digest(self.headers.get('X-Map-CSRF',''),self.server.token):
            self.respond(403,{'error':'Update must come from this map window'});return
        if self.path.startswith('/api/publication/'):
            self.publication_post();return
        if self.path!='/api/update':self.respond(404,{'error':'Unknown map route'});return
        if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length','0')!='0':
            self.respond(400,{'error':'This update accepts no request body'});return
        if not self.server.lock.acquire(blocking=False):self.respond(409,{'error':'An update is already running'});return
        try:
            result=refresh(self.server.output);self.server.last_error=None;self.respond(200,result)
        except (ValueError,OSError,subprocess.SubprocessError,zipfile.BadZipFile) as error:
            self.server.last_error=str(error);self.respond(502,{'error':str(error)})
        finally:self.server.lock.release()

    def publication_post(self):
        if self.path not in {'/api/publication/save','/api/publication/preview','/api/publication/restore'}:
            self.respond(404,{'error':'Unknown publication action'});return
        if self.headers.get('Transfer-Encoding'):
            self.respond(400,{'error':'Use a bounded JSON request'});return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=1024*1024:raise ValueError('Choices must be a bounded JSON request')
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError('Publication requests must be objects')
        except (ValueError,TypeError):self.respond(400,{'error':'Invalid publication request'});return
        if not self.server.lock.acquire(blocking=False):self.respond(409,{'error':'Another operation is running'});return
        try:
            if self.path.endswith('/save'):result=self.server.owner.save(payload['settings'],payload['expectedRevision'])
            elif self.path.endswith('/restore'):result=self.server.owner.restore(payload['expectedRevision'])
            else:result=self.server.owner.preview(payload['settings'],payload['target'])
            self.respond(200,result)
        except Conflict as error:self.respond(409,{'error':str(error)})
        except (ValueError,OSError,KeyError,zipfile.BadZipFile) as error:self.respond(400,{'error':str(error)})
        finally:self.server.lock.release()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path(__file__).with_name('index.html'));p.add_argument('--once',action='store_true');p.add_argument('--open',action='store_true');p.add_argument('--port',type=int,default=0);p.add_argument('--settings',type=Path,help='Owner visibility choices; defaults to the checkout configuration');p.add_argument('--skip-refresh',action='store_true',help=argparse.SUPPRESS);args=p.parse_args()
    output=args.output.expanduser().absolute()
    startup_error=None
    if not args.skip_refresh:
        try:print(json.dumps(refresh(output)))
        except (ValueError,OSError,subprocess.SubprocessError,zipfile.BadZipFile) as error:
            startup_error=str(error);print(startup_error)
            if args.once or not output.is_file():return 1
    if args.once:return 0
    server=MapServer(output,args.port,args.settings);server.last_error=startup_error;print('Skills Estate map: '+server.origin,flush=True)
    if args.open:webbrowser.open(server.origin)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0

if __name__=='__main__':raise SystemExit(main())
