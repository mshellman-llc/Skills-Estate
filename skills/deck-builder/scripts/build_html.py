#!/usr/bin/env python3
"""Build a standalone deck from sourced slide data and a canonical brand profile."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
from visuals import render_visual

ROOT = Path(__file__).resolve().parents[1]


def runtime():
    for p in [ROOT/'_runtime/brand-renderer', ROOT.parent/'brand-renderer']:
        if (p/'brand/html_profile.py').is_file():
            sys.path.insert(0, str(p/'brand'))
            return p
    raise ValueError('Brand runtime is missing. Rebuild the portable package.')


def words(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label+' needs text')
    return html.escape(value, quote=True)


def para(value, label):
    return '<p>'+words(value, label)+'</p>'


def render(data, profile=None):
    runtime()
    from html_profile import resources
    from brand_profile import load_profile
    res = resources(profile)
    brand = load_profile(res['profile'])
    title = words(data.get('title'), 'title')
    context = words(data.get('context'), 'context')
    slides = data.get('slides')
    sources = data.get('sources')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Supply the source records used by the slides')
    for key, value in sources.items():
        words(key, 'source key'); words(value, 'source description')
    if not isinstance(slides, list) or not slides:
        raise ValueError('A deck needs slides')
    source_items = list(sources.items())
    slides = list(slides)
    for start in range(0, len(source_items), 4):
        group = source_items[start:start+4]
        slides.append({'title':'Source records '+str(start//4+1), 'sources':[key for key,value in group], 'blocks':[{'type':'table','headers':['Key','Source record'],'rows':[[key,value] for key,value in group]}]})
    parts=[]
    for i, slide in enumerate(slides, 1):
        if not isinstance(slide, dict): raise ValueError('Each slide must be an object')
        heading=words(slide.get('title'), 'slide title')
        refs=slide.get('sources')
        if not isinstance(refs, list) or not refs or any(not isinstance(x,str) or x not in sources for x in refs):
            raise ValueError('Every slide needs existing source keys')
        blocks=slide.get('blocks')
        if not isinstance(blocks,list) or not blocks: raise ValueError('A slide needs content blocks')
        body=''
        for block_index, block in enumerate(blocks):
            kind=block.get('type')
            if kind in ('sequence','diagram','specimen','bars'):
                body+=render_visual(block,f'slide-{i}-visual-{block_index}')
            elif kind=='text': body+=para(block.get('text'), 'paragraph')
            elif kind=='columns':
                items=block.get('items')
                if not isinstance(items,list) or not 2<=len(items)<=3: raise ValueError('Columns need two or three items')
                body+='<div class="columns">'+''.join('<article><h3>'+words(x.get('title'),'column heading')+'</h3>'+para(x.get('text'),'column text')+'</article>' for x in items)+'</div>'
            elif kind=='flow':
                items=block.get('items')
                if not isinstance(items,list) or not 2<=len(items)<=5: raise ValueError('Flow needs two to five steps')
                body+='<ol class="flow">'+''.join('<li><h3>'+words(x.get('title'),'step heading')+'</h3>'+para(x.get('text'),'step description')+'</li>' for x in items)+'</ol>'
            elif kind=='table':
                headers=block.get('headers');rows=block.get('rows')
                if not isinstance(headers,list) or not headers or not isinstance(rows,list) or not rows: raise ValueError('Table needs headers and rows')
                if any(not isinstance(row,list) or len(row)!=len(headers) for row in rows):raise ValueError('Table rows must match the headers')
                body+='<table><thead><tr>'+''.join('<th scope="col">'+words(x,'header')+'</th>' for x in headers)+'</tr></thead><tbody>'
                body+=''.join('<tr>'+''.join('<td data-label="'+words(headers[j],'header')+'">'+words(x,'cell')+'</td>' for j,x in enumerate(row))+'</tr>' for row in rows)+'</tbody></table>'
            else: raise ValueError('Unknown block type: '+str(kind))
        tag='h1' if i==1 else 'h2'
        source_text='Source: '+', '.join(refs)
        note=('<aside class="implication">'+words(slide['implication'],'implication')+'</aside>') if slide.get('implication') else ''
        lead=para(slide['lead'],'slide lead') if slide.get('lead') else ''
        if 'lead' in slide and not isinstance(slide['lead'],str):raise ValueError('slide lead must be text')
        parts.append(f'<section class="slide" id="slide-{i}" aria-labelledby="title-{i}"><header><span class="context">{context}</span><span>{i:02d} / {len(slides):02d}</span></header><{tag} id="title-{i}">{heading}</{tag}>'+lead+'<div class="body">'+body+'</div>'+note+'<footer>'+html.escape(source_text)+'</footer></section>')
    css=(ROOT/'assets/deck.css').read_text()
    logo = '<img class="logo" alt="Selected project logo" src="'+res['logo']+'">' if res['logo'] else ''
    result='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title><style>'+res['fonts']+res['palette']+f":root{{--slide-body:{max(18,brand['type'].get('slide_min_pt',18))*4/3}px;}}"+css+'</style></head><body>'+logo+'<main>'+''.join(parts)+'</main></body></html>'
    return result, res


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--profile',type=Path)
    a=p.parse_args()
    try:
        result,res=render(json.loads(a.input.read_text()),a.profile)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x') as f:f.write(result)
        print(json.dumps({'output':str(a.output.resolve()),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'profile':res['name'],'profile_sha256':hashlib.sha256(Path(res['profile']).read_bytes()).hexdigest()}))
        return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:
        print(str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
