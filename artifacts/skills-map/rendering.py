"""Render the standalone explorer without importing repository-only tooling."""
import base64
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
DOWNLOADS = re.compile(r'<!--downloads-->.*?<!--/downloads-->|/\*downloads\*/.*?/\*/downloads\*/', re.S)


def render_snapshot(data, output, downloads=True):
    template = (HERE / 'template.html').read_text()
    if not downloads:
        template = DOWNLOADS.sub('', template)
    else:
        for marker in ('<!--downloads-->', '<!--/downloads-->', '/*downloads*/', '/*/downloads*/'):
            template = template.replace(marker, '')
    encode = lambda value: json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    routes = data.get('workflows', json.loads((HERE / 'workflows.json').read_text()))
    style = (HERE / 'explorer.css').read_text()
    for font in (HERE / 'assets').glob('inter-*.ttf'):
        style = style.replace('assets/' + font.name, 'data:font/ttf;base64,' + base64.b64encode(font.read_bytes()).decode())
    Path(output).write_text(template.replace('__ESTATE_DATA__', encode(data)).replace('__ESTATE_ROUTES__', encode(routes)).replace('__ESTATE_STYLE__', style))
