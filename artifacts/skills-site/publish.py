#!/usr/bin/env python3
"""Atomically publish a verified page release to the generated site-publication branch."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

REPOSITORY = 'mshellman-llc/Skills-Estate'
BRANCH = 'site-publication'
FILES = ('private.html', 'public.html', 'catalog.json')


def read_release(directory, source):
    directory = Path(directory)
    manifest = json.loads((directory / 'release.json').read_text())
    if not re.fullmatch(r'[0-9a-f]{40}', source) or manifest.get('format') != 1 or manifest.get('sourceCommit') != source or set(manifest.get('files', {})) != set(FILES):
        raise ValueError('The page release must belong to the verified source commit')
    files = {'release.json': (directory / 'release.json').read_bytes()}
    for name in FILES:
        data = (directory / name).read_bytes()
        record = manifest['files'][name]
        if len(data) > 4_000_000 or record.get('bytes') != len(data) or record.get('sha256') != hashlib.sha256(data).hexdigest():
            raise ValueError('Page release hash or size mismatch: ' + name)
        files[name] = data
    return manifest, files


def publish(api, manifest, files):
    source = manifest['sourceCommit']
    prefix = '/repos/' + REPOSITORY
    try:
        old = api('GET', prefix + '/git/ref/heads/' + BRANCH)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        old = None
    previous = old['object']['sha'] if old else None
    if previous:
        old_file = api('GET', prefix + '/contents/release.json?ref=' + previous)
        old_manifest = json.loads(base64.b64decode(old_file['content']))
        if old_manifest['sourceCommit'] == source:
            if old_manifest != manifest:
                raise ValueError('The same source commit already has different published bytes')
            return {'published': False, 'publicationCommit': previous, 'sourceCommit': source}
        comparison = api('GET', prefix + '/compare/' + old_manifest['sourceCommit'] + '...' + source)
        if comparison['status'] == 'behind':
            return {'published': False, 'reason': 'A newer source is already published', 'publicationCommit': previous, 'sourceCommit': old_manifest['sourceCommit']}
        if comparison['status'] != 'ahead':
            raise ValueError('Page publication source history diverged')
    tree = []
    for name, content in files.items():
        blob = api('POST', prefix + '/git/blobs', {'content': base64.b64encode(content).decode(), 'encoding': 'base64'})
        tree.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    tree_sha = api('POST', prefix + '/git/trees', {'tree': tree})['sha']
    commit = api('POST', prefix + '/git/commits', {'message': 'Publish complete Skills Estate pages from ' + source, 'tree': tree_sha, 'parents': [previous] if previous else []})['sha']
    if previous:
        api('PATCH', prefix + '/git/refs/heads/' + BRANCH, {'sha': commit, 'force': False})
    else:
        api('POST', prefix + '/git/refs', {'ref': 'refs/heads/' + BRANCH, 'sha': commit})
    return {'published': True, 'publicationCommit': commit, 'sourceCommit': source}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path)
    args = parser.parse_args()
    if os.environ.get('GITHUB_REPOSITORY') != REPOSITORY or os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise ValueError('Only the Skills Estate main workflow can publish these pages')
    manifest, files = read_release(args.directory, os.environ.get('GITHUB_SHA', ''))

    def api(method, path, body=None):
        request = urllib.request.Request('https://api.github.com' + path,
            data=json.dumps(body).encode() if body is not None else None, method=method,
            headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'skills-estate-site-publisher'})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    print(json.dumps(publish(api, manifest, files)))


if __name__ == '__main__':
    main()
