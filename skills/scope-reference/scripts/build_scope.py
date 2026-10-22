#!/usr/bin/env python3
"""Build a reconciled static scope reference with the selected canonical profile."""
import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import html
import json
from pathlib import Path
import sys
from scope_reference_validate import load, reconcile, amount, require
ROOT=Path(__file__).resolve().parents[1]
LABELS={'in':'Included','available':'Available','optional':'Optional','out':'Not included'}

def esc(value):return html.escape(str(value),quote=True)
def num(value):return format(amount(value,'number').normalize(),'f')
def money(value,currency):return esc(currency)+' '+format(amount(value,'revenue'),',.2f')

def runtime():
    for p in [ROOT/'_runtime/brand-renderer',ROOT.parent/'brand-renderer']:
        if (p/'brand/html_profile.py').is_file():sys.path.insert(0,str(p/'brand'));return
    raise ValueError('Brand runtime is missing. Assemble the portable package first.')

def render(source,plan,profile=None):
    report=reconcile(source,plan);runtime()
    from html_profile import resources
    res=resources(profile)
    options=plan['options'];quotes={q['id']:q for q in source['quotes']}
    summaries=[]
    for option in options:
        qid=option['quote_id'];counts=report['counts'][qid];snaprows=[]
        for snapshot in option['snapshots']:
            exact=money(snapshot['revenue'],snapshot['currency'])
            if plan.get('rounding',1)==1000:
                rounded=(amount(snapshot['revenue'],'revenue')/1000).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*1000
                price='About '+esc(snapshot['currency'])+' '+format(rounded,',.0f')+'<small>Exact quote: '+exact+'</small>'
            else:price=exact
            active=snapshot['id']==quotes[qid]['active_snapshot_id']
            snaprows.append('<tr data-snapshot="'+esc(snapshot['id'])+'"><th scope="row">'+esc(snapshot['label'])+('<small>Active plan</small>' if active else '')+'</th><td class="price" data-revenue="'+esc(snapshot['revenue'])+'">'+price+'</td><td>'+num(snapshot['weeks'])+' weeks<small>'+num(snapshot['hours'])+' staffing hours</small></td></tr>')
        summaries.append('<article class="option" data-quote="'+esc(qid)+'"><h2>'+esc(option['name'])+'</h2><p class="quote-id">'+esc(qid)+'</p><p>'+esc(option['summary'])+'</p><p class="counts">'+str(counts['in'])+' included · '+str(counts['optional'])+' optional · '+str(counts['available'])+' available</p><table class="plans"><caption>Staffing plans</caption><thead><tr><th>Plan</th><th>Quote price</th><th>Duration</th></tr></thead><tbody>'+''.join(snaprows)+'</tbody></table></article>')
    categories={}
    for item in plan['matrix']:categories.setdefault(item['category'],[]).append(item)
    matrix=[]
    for category,items in categories.items():
        matrix.append('<tr class="category"><th colspan="'+str(len(options)+1)+'">'+esc(category)+'</th></tr>')
        for item in items:
            row='<tr data-item="'+esc(item['id'])+'"><th scope="row"><span>'+esc(item['name'])+'</span><p>'+esc(item['description'])+'</p></th>'
            for option in options:
                qid=option['quote_id'];cell=item['cells'][qid];state=cell['state']
                row+='<td data-quote="'+esc(qid)+'" data-state="'+state+'" data-hours="'+('' if cell['hours'] is None else esc(cell['hours']))+'"><span class="state '+state+'">'+LABELS[state]+'</span>'
                if cell['hours'] is not None:row+='<span class="hours">'+num(cell['hours'])+' h</span>'
                row+='</td>'
            matrix.append(row+'</tr>')
    notes=source.get('notes',[])
    require(isinstance(notes,list) and all(isinstance(v,str) and v.strip() for v in notes),'Notes must be text')
    notehtml=('<section class="notes"><h2>Scope conditions</h2>'+''.join('<p>'+esc(n)+'</p>' for n in notes)+'</section>') if notes else ''
    logo='<img class="logo" alt="Selected project logo" src="'+res['logo']+'">' if res['logo'] else ''
    kind='Synthetic example · ' if source['kind']=='synthetic' else ''
    summary='<section class="options '+('single' if len(options)==1 else 'comparison')+'">'+''.join(summaries)+'</section>'
    table='<section class="scope '+('single-scope' if len(options)==1 else 'comparison-scope')+'"><h2>Scope by item</h2><p>Hours are estimated for each item and option. The staffing plans above set the quote prices.</p><div class="table-scroll" tabindex="0" role="region" aria-label="Scope comparison table"><table class="matrix"><thead><tr><th scope="col">Scope item</th>'+''.join('<th scope="col">'+esc(o['name'])+'</th>' for o in options)+'</tr></thead><tbody>'+''.join(matrix)+'</tbody></table></div><p class="scroll-hint">Scroll the table horizontally on a narrow screen.</p><dl class="legend"><dt>Included</dt><dd>Selected in this quote.</dd><dt>Optional</dt><dd>Optional work; confirm whether to include it.</dd><dt>Available</dt><dd>Not selected. Adding it may change the price or schedule.</dd><dt>Not included</dt><dd>Not part of this option.</dd></dl></section>'
    css=(ROOT/'assets/scope.css').read_text()
    doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scope reference</title><style>'+res['palette']+res['fonts']+css+'</style></head><body><main><header>'+logo+'<p class="eyebrow">'+kind+esc(plan['client'])+'</p><h1>'+esc(plan['title'])+'</h1><p class="intro">'+esc(plan['intro'])+'</p><p class="asof">Quotes as of '+esc(source['captured_at'][:10])+'</p></header>'+summary+table+notehtml+'<footer>'+esc(plan['client'])+' · Scope reference</footer></main></body></html>'
    return doc,report,res

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('presentation',type=Path);p.add_argument('output',type=Path);p.add_argument('--profile',type=Path);a=p.parse_args()
    try:
        require(not a.output.exists(),'Output exists; choose a new attempt directory')
        receipt=a.output.with_suffix('.reconciliation.json');require(not receipt.exists(),'Receipt already exists')
        doc,report,res=render(load(a.source),load(a.presentation),a.profile)
        report.update(source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),presentation_sha256=hashlib.sha256(a.presentation.read_bytes()).hexdigest(),profile_sha256=hashlib.sha256(Path(res['profile']).read_bytes()).hexdigest(),output_sha256=hashlib.sha256(doc.encode()).hexdigest())
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x') as f:f.write(doc)
        with receipt.open('x') as f:json.dump(report,f,indent=2)
        print(json.dumps({'output':str(a.output.resolve()),'reconciliation':str(receipt.resolve()),'mode':report['mode'],'items':report['items']}));return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:print(str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
