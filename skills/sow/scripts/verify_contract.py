#!/usr/bin/env python3
"""Verify a generated SOW against the selected contract profile and quote.

Checks actual clause text, identity, quote values, preserved scope descriptions,
and build hashes. This checks rendering fidelity, not legal approval.
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

def normalize(text):
    return re.sub(r'\s+',' ',text.replace('’',"'").replace('“','"').replace('”','"')).strip()

def money(value):
    return '$'+f'{value:,.2f}'.rstrip('0').rstrip('.')

def verify(document, contract_file, quote_file, variant):
    contract=json.loads(contract_file.read_text()); quote=json.loads(quote_file.read_text())
    with zipfile.ZipFile(document) as archive:
        parts=[name for name in archive.namelist() if re.fullmatch(r'word/(document|header\d*|footer\d*)\.xml',name)]
        text=' '.join(' '.join(''.join(p.itertext()) for p in ET.fromstring(archive.read(name)).findall('.//w:p',NS)) for name in parts)
    text=normalize(text)
    errors=[];checked=[]
    def check(name, value):
        checked.append(name)
        if normalize(str(value)) not in text:errors.append('Missing or changed: '+name)
    is_assess=variant in ('assess','assessment');is_loe=variant=='loe'
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
        keys += ['FIXED_CLOSE','FIXED_INVOICES'] if quote['pricingModel']=='fixed' else ['TM_CLOSE','TM_UPFRONT']
        if not is_assess:keys+=['DEFECT_SEVERITY_INTRO','DEFECT_GONOGO']
    substitutions={'PROVIDER':contract['provider']['legalName'],'CLIENT':quote['projectContext']['accountName'],
        'N':str(quote['projectSummary']['durationWeeks']), 'TOTAL':money(quote['projectSummary']['totalValue']),
        'UPFRONT_PERCENT':str(contract['upfrontPercent']),
        'UPFRONT':money(round(quote['projectSummary']['totalValue']*contract['upfrontPercent']/100,2)),
        'DATE':quote['projectContext'].get('returnBy','')}
    def strings(value, label):
        if isinstance(value,str):yield label,value
        elif isinstance(value,list):
            for i,item in enumerate(value):yield from strings(item,label+'.'+str(i))
        elif isinstance(value,dict):
            for key,item in value.items():yield from strings(item,label+'.'+key)
    for key in keys:
        value=contract['clauses'].get(key)
        if value is None:errors.append('Missing contract key: '+key);continue
        if key=='PROTECTIVE_ASSUMPTIONS' and is_assess:
            value=[x for x in value if not re.search(r'AppExchange|Additional time to conduct workshops',x,re.I)]
        if key=='MISC_TERMS' and is_loe:
            value=[x for x in value if re.search(r'Order of Precedence|Limited Modification',x['title'])]
        for label,line in strings(value,key):
            for token,replacement in substitutions.items():line=line.replace('{'+token+'}',replacement)
            if re.search(r'\{[A-Z_]+\}',line):errors.append('Unresolved contract token: '+label)
            check(label,line)
    check('provider identity',contract['provider']['legalName'])
    check('client identity',quote['projectContext']['accountName'])
    check('quote value',money(quote['projectSummary']['totalValue']))
    def walk(node):
        for item in node.get('scopeItems',[]):
            check('scope name '+item['name'],item['name'])
            description=unescape(re.sub('<[^>]+>',' ',item.get('description','')))
            check('scope description '+item['name'],description)
        for child in node.get('children',[]):walk(child)
    for node in quote['scopeItemsByCapability']:walk(node)
    if not is_loe:
        for phase in quote['timeline']['bands'][0]['phases']:
            check('phase name '+phase['name'],phase['name'])
            check('phase purpose '+phase['name'],phase['purpose'])
        for resource in quote['timeline']['bands'][0]['resources']:
            check('role responsibility '+resource['role'],resource['responsibility'])
        for item in quote['deliverables']:
            for key in ('name','description','format'):
                check('deliverable '+item['name']+' '+key,item[key])
        for exclusion in quote.get('exclusions',[]):check('exclusion',exclusion)
    if '[FLAG:' in text:errors.append('Unresolved input flags in document')
    if contract['status']=='example':check('synthetic label','Synthetic example for skill testing')
    receipt_path=Path(str(document)+'.build.json')
    if not receipt_path.exists():errors.append('Missing build record')
    else:
        receipt=json.loads(receipt_path.read_text())
        for key,file in [('modelSha256',quote_file),('contractSha256',contract_file),('artifactSha256',document)]:
            if receipt.get(key)!=hashlib.sha256(file.read_bytes()).hexdigest():errors.append('Build hash mismatch: '+key)
        if receipt.get('unresolved'):errors.append('Build record contains unresolved inputs')
        if not receipt.get('reconciliation',{}).get('tie'):errors.append('Quote reconciliation did not pass')
        if receipt.get('variant')!=variant:errors.append('Variant differs from build record')
    return {'artifact':str(document),'variant':variant,'checks':len(checked),'failures':errors,'passed':not errors}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document',type=Path)
    parser.add_argument('--contract',required=True,type=Path)
    parser.add_argument('--quote',required=True,type=Path)
    parser.add_argument('--variant',choices=['waterfall','agile','assess','assessment','loe'],required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:report=verify(args.document,args.contract,args.quote,args.variant)
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,ET.ParseError) as exc:
        report={'passed':False,'failures':[str(exc)]}
    rendered=json.dumps(report,indent=2)+'\n';print(rendered)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered)
    raise SystemExit(0 if report['passed'] else 1)
