#!/usr/bin/env python3
"""Reconcile a scope presentation to captured quote and timeline records."""
import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

STATES = {'in', 'available', 'optional', 'out'}

def require(ok, message):
    if not ok: raise ValueError(message)

def text(value, name):
    require(isinstance(value,str) and bool(value.strip()), name+' needs text')
    return value

def amount(value, name):
    require(not isinstance(value,bool) and isinstance(value,(str,int,float,Decimal)),name+' must be numeric')
    try: d=Decimal(str(value))
    except InvalidOperation: raise ValueError(name+' must be numeric')
    require(d.is_finite() and d>=0,name+' must be finite and nonnegative')
    return d

def estimate(item, name, unestimated_allowed):
    """Return a canonical estimate: a Decimal, a low/expected/high range, or None when unestimated."""
    status=item.get('status','estimated')
    require(status in {'estimated','unestimated'},name+' status must be estimated or unestimated')
    hours=item.get('hours')
    if status=='unestimated':
        require(unestimated_allowed,name+' is unestimated; only an unpriced comparison can carry unestimated work')
        require(hours is None,name+' is unestimated and cannot carry hours')
        text(item.get('discovery'),name+' discovery')
        return None
    if isinstance(hours,dict):
        require(set(hours)=={'low','expected','high'},name+' range needs exactly low, expected and high')
        low,expected,high=(amount(hours[k],name+' '+k+' hours') for k in ('low','expected','high'))
        require(low<=expected<=high,name+' range must run low <= expected <= high')
        return {'low':low,'expected':expected,'high':high}
    require(hours is not None,name+' hours must be numeric; mark unestimated work with status "unestimated"')
    return amount(hours,name+' hours')

def indexed(items, name, key='id', allow_empty=False):
    require(isinstance(items,list) and (allow_empty or bool(items)),name+' must be a nonempty list')
    result={}
    for item in items:
        require(isinstance(item,dict),name+' entries must be objects')
        identity=text(item.get(key),name+' '+key)
        require(identity not in result,'Duplicate '+name+' ID: '+identity)
        result[identity]=item
    return result

def load(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'Duplicate JSON key: '+key);result[key]=value
        return result
    def invalid(value):raise ValueError('Nonfinite JSON value: '+value)
    return json.loads(Path(path).read_text(),object_pairs_hook=unique,parse_constant=invalid)

def state(item, active):
    return 'optional' if item['optional'] else ('in' if item['id'] in active else 'available')

PRICE_INPUTS=('price','staffing','timeline')

def reconcile(source, plan):
    require(isinstance(source,dict) and isinstance(plan,dict),'Source and presentation must be objects')
    require(source.get('kind') in {'export','live-capture','synthetic'},'Declare the source kind')
    text(source.get('system'),'source system');text(source.get('revision'),'source revision')
    captured=datetime.fromisoformat(text(source.get('captured_at'),'capture time').replace('Z','+00:00'))
    require(captured.tzinfo is not None,'Capture time needs a timezone')
    pricing=source.get('pricing','quoted')
    require(pricing in {'quoted','unpriced'},'Pricing must be quoted or unpriced')
    unpriced=pricing=='unpriced'
    missing=source.get('missing_inputs')
    if unpriced:
        # An unpriced comparison names what is missing; it never derives price, staffing or timeline.
        require(isinstance(missing,dict) and set(missing)==set(PRICE_INPUTS),'An unpriced comparison must name its missing price, staffing and timeline inputs')
        for key in PRICE_INPUTS:text(missing[key],'missing '+key+' input')
    else:require(missing is None,'Missing inputs belong only to an unpriced comparison')
    quotes=indexed(source.get('quotes'),'quote');options=indexed(plan.get('options'),'option','quote_id')
    require(set(quotes)==set(options),'Source quotes and selected options must match exactly; supply a bounded export')
    text(plan.get('title'),'title');text(plan.get('client'),'client');text(plan.get('intro'),'intro')
    require(type(plan.get('rounding',1)) is int and plan.get('rounding',1) in (1,1000),'Rounding must be 1 or 1000')
    truth={};counts={};timelines={};unestimated={}
    for qid,q in quotes.items():
        full=indexed(q.get('full_items'),'scope item')
        active=q.get('active_item_ids')
        require(isinstance(active,list) and all(isinstance(x,str) for x in active),'Active IDs must be strings')
        require(len(active)==len(set(active)) and set(active)<=set(full),'Active IDs must be unique and present in the full scope')
        counts[qid]={s:0 for s in STATES};unestimated[qid]=0
        for key,item in full.items():
            text(item.get('name'),'item name');text(item.get('category'),'item category')
            hours=estimate(item,'Item '+key,unpriced);require(isinstance(item.get('optional'),bool),'Optional flag must be explicit')
            if key in truth:
                require(truth[key]['name']==item['name'] and truth[key]['category']==item['category'],'Conflicting identity for '+key+'; reconcile the source mapping')
            else:truth[key]={'name':item['name'],'category':item['category'],'cells':{}}
            s=state(item,active);truth[key]['cells'][qid]={'hours':hours,'state':s,'unestimated':hours is None};counts[qid][s]+=1
            unestimated[qid]+=hours is None
        if unpriced:
            require(q.get('snapshots',[])==[] and q.get('active_snapshot_id') is None,'An unpriced comparison carries no snapshots: '+qid)
            require(options[qid].get('snapshots',[])==[],'An unpriced comparison cannot display a snapshot: '+qid)
            text(options[qid].get('name'),'option name');text(options[qid].get('summary'),'option summary')
            timelines[qid]={};continue
        snaps=indexed(q.get('snapshots'),'snapshot')
        active_snapshot=text(q.get('active_snapshot_id'),'active snapshot')
        require(active_snapshot in snaps,'Active snapshot is missing: '+qid)
        requested=indexed(options[qid].get('snapshots'),'display snapshot')
        require(active_snapshot in requested,'Display must include the active snapshot: '+qid)
        require(set(requested)<=set(snaps),'Display snapshot is absent from the source: '+qid)
        text(options[qid].get('name'),'option name');text(options[qid].get('summary'),'option summary')
        for sid,display in requested.items():
            actual=snaps[sid]
            for field in ('revenue','weeks','hours'):
                require(amount(actual.get(field),field)==amount(display.get(field),field),'Snapshot '+field+' mismatch: '+qid+'/'+sid)
            require(bool(re.fullmatch('[A-Z]{3}',text(actual.get('currency'),'currency'))),'Currency needs a three-letter code')
            require(display.get('currency')==actual['currency'],'Snapshot currency mismatch')
            require(display.get('label')==text(actual.get('label'),'snapshot label'),'Snapshot label mismatch')
        timelines[qid]=requested
    draft=indexed(plan.get('matrix'),'presentation item')
    require(set(draft)==set(truth),'Presentation must contain every source item exactly once')
    for key,item in draft.items():
        actual=truth[key]
        require(item.get('name')==actual['name'],'Item name mismatch: '+key)
        require(item.get('category')==actual['category'],'Item category mismatch: '+key)
        text(item.get('description'),'description')
        basis=item.get('description_basis');require(isinstance(basis,dict),'Description needs a source reference: '+key)
        qid=basis.get('quote_id');field=basis.get('field')
        require(qid in quotes and field in {'description','effort_basis'},'Invalid description reference: '+key)
        original=next((v for v in quotes[qid]['full_items'] if v['id']==key),None)
        require(original is not None,'Description source item is absent: '+key)
        text(original.get(field),'description source text')
        cells=item.get('cells');require(isinstance(cells,dict) and set(cells)==set(options),'Every item needs one cell per option')
        for qid,cell in cells.items():
            require(isinstance(cell,dict),'Cells must be objects')
            expected=actual['cells'].get(qid,{'hours':None,'state':'out','unestimated':False})
            require(cell.get('state') in STATES and cell['state']==expected['state'],'State mismatch: '+key+'/'+qid)
            if expected['unestimated']:
                require(cell.get('status')=='unestimated' and cell.get('hours') is None,'Unestimated work must stay unestimated, never zero: '+key+'/'+qid)
            elif expected['hours'] is None:require(cell.get('hours') is None and 'status' not in cell,'Absent items cannot carry hours: '+key+'/'+qid)
            else:
                require(cell.get('status','estimated')=='estimated','Estimate status mismatch: '+key+'/'+qid)
                require(estimate(cell,'Display cell '+key+'/'+qid,False)==expected['hours'],'Hours mismatch: '+key+'/'+qid)
    for qid in options:counts[qid]['out']=sum(qid not in row['cells'] for row in truth.values())
    return {'ok':True,'mode':'single-option' if len(options)==1 else 'comparison','pricing':pricing,'counts':counts,'unestimated':unestimated,'items':len(truth),'quotes':len(quotes),'source_kind':source['kind'],'source_revision':source['revision'],'captured_at':source['captured_at']}

# Retain the original promised import API for older callers. Never collapse two names.
def normalize(name,prefix_aliases=None):
    n=text(name,'name').lower()
    for a,b in (prefix_aliases or {}).items():n=n.replace(a.lower(),b.lower())
    return re.sub(r'[^a-z0-9]','',n)

def validate(file_items,source_items,prefix_aliases=None):
    try:
        def keyed(items):
            result={}
            for name,value in items.items():
                key=normalize(name,prefix_aliases);require(key not in result,'Ambiguous normalized name: '+name)
                require(isinstance(value.get('states'),dict) and all(s in STATES for s in value['states'].values()),'Unknown state: '+name)
                result[key]=value
            return result
        a,b=keyed(file_items),keyed(source_items);issues=[]
        if set(a)!=set(b):issues.append('Item sets differ')
        for key in set(a)&set(b):
            if amount(a[key]['hours'],'hours')!=amount(b[key]['hours'],'hours'):issues.append('Hours differ: '+key)
            if a[key]['states']!=b[key]['states']:issues.append('States differ: '+key)
        return not issues,issues
    except (ValueError,TypeError,KeyError) as e:return False,[str(e)]

def present_counts(items):
    result={}
    for item in items.values():
        for option,s in item['states'].items():
            require(s in STATES,'Unknown state: '+str(s));result.setdefault(option,0)
            if s!='out':result[option]+=1
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('presentation');a=p.parse_args()
    try:print(json.dumps(reconcile(load(a.source),load(a.presentation)),indent=2));return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:print(str(e));return 2
if __name__=='__main__':raise SystemExit(main())
