#!/usr/bin/env python3
"""Build a standalone proposal or scope explorer from sourced option data."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
from brand_runtime import apply_profile, roadmap_assets


def require_text(value, label):
    if not isinstance(value,str) or not value.strip():
        raise ValueError('Missing text: '+label)


def validate(data,quote=None):
    meta=data.get('meta',{})
    for key in ('client','opportunity','prepared_by','date','validity','confidentiality'):
        require_text(meta.get(key),'meta.'+key)
    mode=meta.get('mode')
    if mode not in ('proposal','explorer'):
        raise ValueError('meta.mode must be proposal or explorer')
    versions=data.get('versions')
    if not isinstance(versions,list) or not versions:
        raise ValueError('At least one sourced version is required')
    keys=[v.get('key') for v in versions]
    if any(not isinstance(k,str) or not re.fullmatch('[A-Za-z0-9_-]+',k) for k in keys) or len(set(keys))!=len(keys):
        raise ValueError('Version keys must be unique letters, digits, hyphens or underscores')
    sources=data.get('sources')
    if not isinstance(sources,list) or not sources:
        raise ValueError('Sources are required')
    source_ids=set()
    for source in sources:
        for key in ('id','title','reference','revision'):
            require_text(source.get(key),'source.'+key)
        if source['id'] in source_ids:raise ValueError('Source IDs must be unique')
        source_ids.add(source['id'])
    all_items={}
    for version in versions:
        for key in ('name','tagline','source'):
            require_text(version.get(key),'version.'+key)
        if version['source'] not in source_ids:raise ValueError('Unknown version source')
        included=[]
        if not isinstance(version.get('scope_sections'),list) or not version['scope_sections']:
            raise ValueError('Version needs scope_sections')
        for section in version['scope_sections']:
            require_text(section.get('title'),'scope section title')
            if not isinstance(section.get('items'),list) or not section['items']:
                raise ValueError('Scope section needs items')
            for item in section['items']:
                for key in ('id','name','description','source'):
                    require_text(item.get(key),'scope item.'+key)
                if not re.fullmatch('[A-Za-z0-9_-]+',item['id']):
                    raise ValueError('Scope IDs must contain only letters, digits, hyphens or underscores')
                if item['source'] not in source_ids:raise ValueError('Unknown scope source')
                if item['id'] in included:raise ValueError('Duplicate scope ID within version')
                included.append(item['id'])
                normalized={**item,'section':section['title']}
                if item['id'] in all_items and all_items[item['id']]!=normalized:
                    raise ValueError('Shared scope ID has conflicting wording: '+item['id'])
                all_items[item['id']]=normalized
        if not isinstance(version.get('assumptions'),list) or not version['assumptions']:
            raise ValueError('Version needs sourced assumptions')
        for text in version['assumptions']:require_text(text,'assumption')
        if not isinstance(version.get('not_included'),list):raise ValueError('Version needs not_included list')
        for boundary in version['not_included']:
            require_text(boundary.get('item'),'boundary item')
            require_text(boundary.get('route'),'boundary route')
        if mode=='explorer':
            if any(k in version for k in ('total','duration_weeks','team','timeline')):
                raise ValueError('Explorer cannot include price, duration, team or timeline')
            if type(version.get('metric')) is not int or version['metric']!=len(included):
                raise ValueError('Explorer metric must equal the count of distinct included scope IDs')
            require_text(version.get('metric_label'),'metric_label')
        version['_included_ids']=included
    for version in versions:
        routes={x['item']:x['route'] for x in version['not_included']}
        for item in all_items.values():
            if item['id'] not in version['_included_ids'] and item['name'] not in routes:
                raise ValueError('Excluded scope needs a route: '+item['name'])
    if mode=='proposal':
        if not quote:raise ValueError('Proposal mode needs --quote with the source quote export')
        for key in ('quote_number','currency'):require_text(meta.get(key),'meta.'+key)
        if not re.fullmatch('[A-Z]{3}',meta['currency']):
            raise ValueError('Currency must be an uppercase three-letter code')
        if meta['quote_number']!=quote.get('quote_number') or meta['currency']!=quote.get('currency'):
            raise ValueError('Quote identity or currency differs from source')
        quote_versions=quote.get('versions')
        if not isinstance(quote_versions,list) or not quote_versions:
            raise ValueError('Quote needs a nonempty versions list')
        quoted={v['key']:v for v in quote_versions}
        if len(quoted)!=len(quote_versions):
            raise ValueError('Quote version keys must be unique')
        if set(quoted)!=set(keys):raise ValueError('Proposal options differ from the quote')
        fields=('name','tagline','total','duration_weeks','team','timeline','scope_sections','assumptions','not_included')
        for version in versions:
            for field in fields:
                if field not in version or version[field]!=quoted[version['key']].get(field):
                    raise ValueError('Quote mismatch: '+version['key']+'.'+field)
            if type(version['total']) not in (int,float) or not 0<=version['total']<1e15:
                raise ValueError('Quote total must be a finite nonnegative number')
            if type(version['duration_weeks']) not in (int,float) or not math.isfinite(version['duration_weeks']) or version['duration_weeks']<=0:
                raise ValueError('Quote duration must be positive')
            for field in ('team','timeline'):
                if not isinstance(version[field],list) or not version[field]:
                    raise ValueError('Quote needs a nonempty '+field+' list')
            for member in version['team']:
                for key in ('role','allocation'):require_text(member.get(key),'team.'+key)
            for phase in version['timeline']:
                for key in ('phase','weeks'):require_text(phase.get(key),'timeline.'+key)
    else:
        if 'currency' in meta:raise ValueError('Explorer has no currency field')
        require_text(data.get('counting_method'),'counting_method')
        phase=data.get('phase_zero',{})
        for key in ('name','description'):require_text(phase.get(key),'phase_zero.'+key)
        if not isinstance(phase.get('outputs'),list) or not phase['outputs']:
            raise ValueError('Next step needs its outputs')
        for item in phase['outputs']:require_text(item,'phase_zero output')
        serialized=json.dumps(data,ensure_ascii=False)
        if re.search(r'[$€£¥₹]|\b(?:USD|EUR|GBP|JPY|CAD|AUD|INR)\b',serialized,re.I):
            raise ValueError('Explorer contains currency')
    if not isinstance(data.get('next_steps'),list) or not data['next_steps']:
        raise ValueError('Named next steps are required')
    for step in data['next_steps']:require_text(step,'next step')
    for decision in data.get('decisions',[]):
        for key in ('question','owner','source'):require_text(decision.get(key),'decision.'+key)
        if decision['source'] not in source_ids:raise ValueError('Unknown decision source')
    data['_scope_items']=list(all_items.values())
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--quote',type=Path)
    parser.add_argument('--profile',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists() or args.output.with_suffix('.build.json').exists():
        parser.error('Output exists; choose a new attempt')
    try:
        data=validate(json.loads(args.input.read_text()),json.loads(args.quote.read_text()) if args.quote else None)
        template=(HERE.parent/'templates/proposal.html').read_text()
        # JSON must not terminate its script element or become executable markup.
        encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        kit=roadmap_assets(str(args.profile) if args.profile else None)
        html=template.replace('__PROPOSAL_DATA__',encoded).replace('__RK_CSS__',kit['css']).replace('__RK_JS__',kit['js'])
        html,brand=apply_profile(html,str(args.profile) if args.profile else None)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(html)
        receipt={'mode':data['meta']['mode'],'state':'built; browser and source review required',
                 'inputSha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),
                 'quoteSha256':hashlib.sha256(args.quote.read_bytes()).hexdigest() if args.quote else None,
                 'profileSha256':hashlib.sha256(Path(brand['profile']).read_bytes()).hexdigest(),
                 'artifactSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                 'versions':len(data['versions'])}
        args.output.with_suffix('.build.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt,indent=2))
    except (ValueError,KeyError,TypeError,OSError) as error:
        parser.exit(2,str(error)+'\n')

if __name__=='__main__':main()
