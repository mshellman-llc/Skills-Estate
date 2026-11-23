#!/usr/bin/env python3
"""Verify a statement of work against the selected contract profile and quote.

Checks actual clause text, identity, quote values and preserved scope descriptions.
In the default (generator) mode it also checks the build record: input and artifact
hashes, the three-way tie and, for an example profile, the label the generator
prints ("Synthetic example for skill testing"). This checks rendering fidelity,
not legal approval.

Token sources. The profile's clause tokens are filled from their own fields:
  {PROVIDER}         contract.provider.legalName
  {CLIENT}           quote projectContext.clientLegalName (the contracting party;
                     accountName is the display name and is checked separately)
  {N}                contract.startWindowDays (days allowed to start after signature)
  {DATE}             quote projectContext.signingDate (not returnBy, the offer expiry)
  {TOTAL}            quote projectSummary.totalValue
  {UPFRONT_PERCENT}  contract.upfrontPercent
  {UPFRONT}          totalValue times upfrontPercent

A null or absent field is unresolved. Each unresolved token is reported as its own
finding and every other check still runs; the text around an unresolved token is
still checked.

--document-route checks a document built with the document tool, or any draft with
no generator build record: clause text, provider and client identities, display
name, quote total and scope. It skips the build record and the generator's example
label, which only the generator writes.

Exit 0 when every check passes, 1 when any finding is reported.
"""
import argparse
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
EXAMPLE_LABEL='Synthetic example for skill testing'
TOKEN_FIELDS={'PROVIDER':'contract provider.legalName','CLIENT':'quote projectContext.clientLegalName',
    'N':'contract startWindowDays','DATE':'quote projectContext.signingDate',
    'TOTAL':'quote projectSummary.totalValue','UPFRONT_PERCENT':'contract upfrontPercent',
    'UPFRONT':'quote projectSummary.totalValue and contract upfrontPercent'}

def normalize(text):
    return re.sub(r'\s+',' ',text.replace('’',"'").replace('“','"').replace('”','"')).strip()

def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool)

def money(value):
    """Dollar text for a number, None for anything unresolved (null, absent, text)."""
    if not number(value):return None
    return '$'+f'{value:,.2f}'.rstrip('0').rstrip('.')

def dig(value,*path):
    """Follow keys and indexes; None when any step is missing or null."""
    for step in path:
        try:value=value[step]
        except (KeyError,IndexError,TypeError):return None
        if value is None:return None
    return value

def strings(value, label):
    if isinstance(value,str):yield label,value
    elif isinstance(value,list):
        for i,item in enumerate(value):yield from strings(item,label+'.'+str(i))
    elif isinstance(value,dict):
        for key,item in value.items():yield from strings(item,label+'.'+key)

def verify(document, contract_file, quote_file, variant, document_route=False):
    contract=json.loads(contract_file.read_text()); quote=json.loads(quote_file.read_text())
    with zipfile.ZipFile(document) as archive:
        parts=[name for name in archive.namelist() if re.fullmatch(r'word/(document|header\d*|footer\d*)\.xml',name)]
        text=' '.join(' '.join(''.join(p.itertext()) for p in ET.fromstring(archive.read(name)).findall('.//w:p',NS)) for name in parts)
    text=normalize(text)
    errors=[];checked=[];unresolved={}
    def unresolve(name,why):
        errors.append('Unresolved input: '+name+' ('+why+')');unresolved[name]=why
    def check(name, value):
        if value is None:unresolve(name,'null or absent in the input');return
        checked.append(name)
        if normalize(str(value)) not in text:errors.append('Missing or changed: '+name)
    is_assess=variant in ('assess','assessment');is_loe=variant=='loe'
    pricing=quote.get('pricingModel')
    if not is_loe and pricing not in ('fixed','tm'):unresolve('pricingModel','needs fixed or tm; its clauses are not checked')
    keys=['PREAMBLE','LOE_FIXED_CLOSE','FIXED_INVOICES','EXPENSES_CARVEOUT','COMMENCEMENT_STAFFING_ASSESS',
          'MISC_TERMS','SIGNATURE_PREAMBLE','AUTHORITY_BIND','LOE_ACCEPTANCE'] if is_loe else [
        'PREAMBLE','NOTICE_SP_LABEL','NOTICE_CLIENT_LABEL','PROJECT_SCOPE_INTRO','OUT_OF_SCOPE_HEADER',
        'CATCH_ALL_EXCLUSION','ELAPSED_PERIOD','CLIENT_RELIANCE','PROTECTIVE_ASSUMPTIONS','LOCATION_OF_SERVICES',
        'EXPENSES_CARVEOUT','REMITTANCE_BILLTO_LABEL','REMITTANCE_PAY_LABEL','REMITTANCE_CHECK','REMITTANCE_ELECTRONIC',
        'DEEMED_ACCEPTANCE','MISC_TERMS','SIGNATURE_PREAMBLE','AUTHORITY_BIND']
    if not is_loe:
        for base in ('COMMENCEMENT_STAFFING','PROJECT_MANAGEMENT_INTRO','PROJECT_MANAGEMENT_BULLETS',
                     'CLIENT_RESOURCES_INTRO','CLIENT_RESOURCES','CLIENT_RESOURCES_NOTE'):
            keys.append(base+('_ASSESS' if is_assess else ''))
        if pricing in ('fixed','tm'):keys += ['FIXED_CLOSE','FIXED_INVOICES'] if pricing=='fixed' else ['TM_CLOSE','TM_UPFRONT']
        if not is_assess:keys+=['DEFECT_SEVERITY_INTRO','DEFECT_GONOGO']
    total=dig(quote,'projectSummary','totalValue');percent=dig(contract,'upfrontPercent')
    substitutions={'PROVIDER':dig(contract,'provider','legalName'),'CLIENT':dig(quote,'projectContext','clientLegalName'),
        'N':None if dig(contract,'startWindowDays') is None else str(contract['startWindowDays']),
        'TOTAL':money(total),
        'UPFRONT_PERCENT':None if percent is None else str(percent),
        'UPFRONT':money(round(total*percent/100,2)) if number(total) and number(percent) else None,
        'DATE':dig(quote,'projectContext','signingDate')}
    substitutions={k:(v if v!='' else None) for k,v in substitutions.items()}
    used={}
    for key in keys:
        value=dig(contract,'clauses',key)
        if value is None:errors.append('Missing contract key: '+key);continue
        if key=='PROTECTIVE_ASSUMPTIONS' and is_assess:
            value=[x for x in value if not re.search(r'AppExchange|Additional time to conduct workshops',x,re.I)]
        if key=='MISC_TERMS' and is_loe:
            value=[x for x in value if re.search(r'Order of Precedence|Limited Modification',x['title'])]
        for label,line in strings(value,key):
            missing=[t for t in re.findall(r'\{([A-Z_]+)\}',line) if t in substitutions and substitutions[t] is None]
            for token in missing:used.setdefault(token,[]).append(label)
            if missing:
                # Keep checking the wording around each unresolved token.
                for token,replacement in substitutions.items():
                    if replacement is not None:line=line.replace('{'+token+'}',replacement)
                for fragment in re.split(r'\{(?:'+'|'.join(k for k,v in substitutions.items() if v is None)+r')\}',line):
                    if fragment.strip():check(label+' (text around an unresolved token)',fragment)
                continue
            for token,replacement in substitutions.items():
                if replacement is not None:line=line.replace('{'+token+'}',replacement)
            if re.search(r'\{[A-Z_]+\}',line):errors.append('Unresolved contract token: '+label)
            check(label,line)
    for token,labels in used.items():
        unresolve('{'+token+'}','null or absent: '+TOKEN_FIELDS[token]+'; used in '+', '.join(sorted(set(labels))))
    check('provider identity',dig(contract,'provider','legalName'))
    if substitutions['CLIENT'] is None:unresolve('client identity','projectContext.clientLegalName is null or absent')
    else:check('client identity',substitutions['CLIENT'])
    check('client display name',dig(quote,'projectContext','accountName'))
    if total is None or not number(total):unresolve('quote value','projectSummary.totalValue is null or absent')
    else:check('quote value',money(total))
    def walk(node):
        for item in node.get('scopeItems') or []:
            name=item.get('name')
            check('scope name '+str(name),name)
            description=item.get('description')
            if description is not None:description=unescape(re.sub('<[^>]+>',' ',description))
            check('scope description '+str(name),description)
        for child in node.get('children') or []:walk(child)
    for node in quote.get('scopeItemsByCapability') or []:walk(node)
    if not is_loe:
        band=dig(quote,'timeline','bands',0) or {}
        for phase in band.get('phases') or []:
            check('phase name '+str(phase.get('name')),phase.get('name'))
            check('phase purpose '+str(phase.get('name')),phase.get('purpose'))
        for resource in band.get('resources') or []:
            check('role responsibility '+str(resource.get('role')),resource.get('responsibility'))
        for item in quote.get('deliverables') or []:
            for key in ('name','description','format'):
                check('deliverable '+str(item.get('name'))+' '+key,item.get(key))
        for exclusion in quote.get('exclusions') or []:check('exclusion',exclusion)
    if '[FLAG:' in text:errors.append('Unresolved input flags in document')
    if not document_route:
        if contract.get('status')=='example':check('synthetic label',EXAMPLE_LABEL)
        receipt_path=Path(str(document)+'.build.json')
        if not receipt_path.exists():errors.append('Missing build record')
        else:
            receipt=json.loads(receipt_path.read_text())
            for key,file in [('modelSha256',quote_file),('contractSha256',contract_file),('artifactSha256',document)]:
                if receipt.get(key)!=hashlib.sha256(file.read_bytes()).hexdigest():errors.append('Build hash mismatch: '+key)
            if receipt.get('unresolved'):errors.append('Build record contains unresolved inputs')
            if not receipt.get('reconciliation',{}).get('tie'):errors.append('Quote reconciliation did not pass')
            if receipt.get('variant')!=variant:errors.append('Variant differs from build record')
    return {'artifact':str(document),'variant':variant,'mode':'document-route' if document_route else 'generator',
        'checks':len(checked),'unresolved':sorted(unresolved),'failures':errors,'passed':not errors}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('document',type=Path)
    parser.add_argument('--contract',required=True,type=Path)
    parser.add_argument('--quote',required=True,type=Path)
    parser.add_argument('--variant',choices=['waterfall','agile','assess','assessment','loe'],required=True)
    parser.add_argument('--document-route',action='store_true',
        help='check a document-tool build or draft: skip the generator build record and example label')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:report=verify(args.document,args.contract,args.quote,args.variant,args.document_route)
    except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile,ET.ParseError) as exc:
        report={'passed':False,'failures':[str(exc)]}
    rendered=json.dumps(report,indent=2)+'\n';print(rendered)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered)
    raise SystemExit(0 if report['passed'] else 1)
