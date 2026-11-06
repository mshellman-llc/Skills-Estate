"""Validate complete task ZIPs from the same passing GitHub run as the map."""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

MAX_BYTES=128*1024*1024

def safe_entries(archive):
    result={}
    for item in archive.infolist():
        name=PurePosixPath(item.filename)
        if name.is_absolute() or '..' in name.parts or '\\' in item.filename or item.filename in result:
            raise ValueError('Unsafe or duplicate package archive path')
        if item.file_size>MAX_BYTES or ((item.external_attr>>16)&0o170000)==0o120000:
            raise ValueError('Unsafe package archive entry')
        result[item.filename]=item
    if sum(x.file_size for x in result.values())>MAX_BYTES:
        raise ValueError('Expanded package archive exceeds its size limit')
    return result

def validate(raw,data):
    if len(raw)>MAX_BYTES:raise ValueError('Package archive exceeds its size limit')
    expected={n for s in data['skills'] for n in s.get('downloadPackages',[])}
    if not expected:raise ValueError('The map has no package download inventory')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries=safe_entries(archive)
        releases=[k for k in entries if PurePosixPath(k).name=='release.json']
        if len(releases)!=1:raise ValueError('Missing or duplicate release manifest')
        release=json.loads(archive.read(releases[0]))
        if set(release.get('packages',{}))!=expected:raise ValueError('Map and task package inventories differ')
        payloads={};packages={}
        for name in sorted(expected):
            item=release['packages'][name]
            if item['file']!=name+'.zip':raise ValueError('Unexpected task package filename')
            matches=[k for k in entries if PurePosixPath(k).name==item['file']]
            if len(matches)!=1:raise ValueError('Missing or duplicate task ZIP')
            payload=archive.read(matches[0])
            if hashlib.sha256(payload).hexdigest()!=item['sha256']:raise ValueError('Task ZIP hash mismatch')
            with zipfile.ZipFile(io.BytesIO(payload)) as inner:
                contents=safe_entries(inner)
                if inner.testzip() is not None:raise ValueError('Corrupt task ZIP')
                if not any(PurePosixPath(p).name=='SKILL.md' for p in contents):raise ValueError('Task ZIP has no entrypoint')
            payloads[item['file']]=payload
            packages[name]={'file':item['file'],'sha256':item['sha256'],'bytes':len(payload)}
    manifest={'commit':data['baseCommit'],'source_sha256':release['source_sha256'],'packages':packages}
    return payloads,manifest

def write(raw,data,destination):
    payloads,manifest=validate(raw,data)
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    for name,payload in payloads.items():(destination/name).write_bytes(payload)
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
