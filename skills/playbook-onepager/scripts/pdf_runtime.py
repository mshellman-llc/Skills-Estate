"""Validate handout inputs and run an isolated browser PDF render."""
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import subprocess


def safe_fields(value):
    """Preserve supported inline emphasis without loading arbitrary source HTML."""
    from markupsafe import Markup

    class Inline(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.output = []
            self.stack = []

        def handle_starttag(self, tag, attrs):
            if tag not in ('span', 'strong', 'b', 'em', 'i', 'br'):
                raise ValueError('Unsupported source HTML tag: ' + tag)
            if attrs and (tag != 'span' or attrs != [('class', 'hl')]):
                raise ValueError('Only span class="hl" is allowed in source HTML')
            self.output.append('<' + tag + (' class="hl"' if attrs else '') + '>')
            if tag != 'br':
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if not self.stack or self.stack.pop() != tag:
                raise ValueError('Unbalanced source HTML')
            self.output.append('</' + tag + '>')

        def handle_data(self, data):
            self.output.append(escape(data))

        def handle_entityref(self, name):
            raise ValueError('Unsupported entity: ' + name)

    if isinstance(value, str):
        parser = Inline()
        parser.feed(value)
        parser.close()
        if parser.stack:
            raise ValueError('Unclosed source HTML')
        return Markup(''.join(parser.output))
    if isinstance(value, list):
        return [safe_fields(item) for item in value]
    if isinstance(value, dict):
        return {key: safe_fields(item) for key, item in value.items()}
    return value


def validate_spec(template, ctx):
    if not isinstance(ctx, dict):
        raise ValueError('Artifact spec must be an object')
    required = ['title', 's1', 's2', 's3', 's4'] if template == 'internal_brief.html' else ['title', 'intro', 'how']
    for key in required:
        if not isinstance(ctx.get(key), str) or not ctx[key].strip():
            raise ValueError('Missing required text: ' + key)
    if template == 'internal_brief.html':
        for choices in (('included_list', 's5'), ('not_included', 'boundary'), ('steps', 's7')):
            if not any(ctx.get(key) for key in choices):
                raise ValueError('Supply ' + ' or '.join(choices))
    elif not ctx.get('what_you_get'):
        raise ValueError('Missing required list: what_you_get')
    for key in ('qualifiers', 'disqualifiers', 'included_list', 'not_included', 'steps', 'what_you_get'):
        if key in ctx and ctx[key] is not None:
            if not isinstance(ctx[key], list) or any(not isinstance(x, str) or not x.strip() for x in ctx[key]):
                raise ValueError(key + ' must contain nonempty text items')
    for key in ('tracks', 'callouts', 'columns'):
        if key in ctx and (not isinstance(ctx[key], list) or any(
                not isinstance(x, dict) or not all(isinstance(x.get(k), str) and x[k].strip() for k in ('k', 'v'))
                for x in ctx[key])):
            raise ValueError(key + ' must contain k/v text objects')


def render_and_check(html_path, pdf_path, expected):
    from pypdf import PdfReader
    node = os.environ.get('ESTATE_NODE') or shutil.which('node')
    if not node:
        raise RuntimeError('Node.js is missing; set ESTATE_NODE')
    roots = [Path(x) for key in ('ESTATE_NODE_MODULES', 'NODE_PATH')
             for x in os.environ.get(key, '').split(os.pathsep) if x]
    roots += [p / 'node_modules' for p in (Path.cwd(), *Path.cwd().parents)]
    entry = next((root / 'playwright' / name for root in roots for name in ('index.mjs', 'index.js')
                  if (root / 'playwright' / name).is_file()), None)
    if not entry:
        raise RuntimeError('Playwright is missing; set ESTATE_NODE_MODULES')
    args = [node, str(Path(__file__).with_name('render_pdf.mjs')), str(html_path.resolve()),
            str(pdf_path.resolve()), str(expected)]
    result = subprocess.run(args, env={**os.environ, 'PW_MODULE': entry.resolve().as_uri()},
                            capture_output=True, text=True, timeout=180)
    pdf_path.with_suffix('.console.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('PDF layout check failed; see ' + str(pdf_path.with_suffix('.checks.json')))
    pages = len(PdfReader(pdf_path).pages)
    if pages != expected:
        raise ValueError(f'PDF has {pages} pages; expected {expected}. Retained for repair.')
    return pages
