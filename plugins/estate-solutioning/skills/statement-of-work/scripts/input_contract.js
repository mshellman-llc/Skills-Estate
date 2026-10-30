'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function readInputs(argv) {
  const [modelFile, variant='waterfall', ...options] = argv;
  const args = {};
  for(let i=0;i<options.length;i++) {
    const key=options[i];
    if(['--example','--draft'].includes(key)) args[key]=true;
    else if(['--contract','--output','--profile'].includes(key) && options[i+1]) args[key]=options[++i];
    else throw new Error('Unknown or incomplete option: '+key);
  }
  if(!modelFile || !args['--contract'] || !args['--output'])
    throw new Error('Usage: generate_sow.js model.json waterfall|agile|assess|loe --contract contract.json --output FILE.docx [--profile brand.md] [--example] [--draft]');
  if(!['waterfall','agile','assess','assessment','loe'].includes(variant)) throw new Error('Unknown variant: '+variant);
  const modelPath=path.resolve(modelFile), contractPath=path.resolve(args['--contract']);
  const model=JSON.parse(fs.readFileSync(modelPath,'utf8'));
  const contract=JSON.parse(fs.readFileSync(contractPath,'utf8'));
  if(args['--profile']) process.env.SKILLS_BRAND_PROFILE=path.resolve(args['--profile']);
  if(!contract.source || !['confirmed','example'].includes(contract.status))
    throw new Error('Contract profile needs a source and confirmed status (or example with --example)');
  if(contract.status==='example' && (!args['--example'] || !model._fixture))
    throw new Error('Example contract profiles require --example and an explicitly synthetic model');
  const provider=contract.provider;
  if(!provider || !provider.legalName || !Array.isArray(provider.noticeAddress) || !provider.noticeAddress.length || !provider.contact)
    throw new Error('Contract profile needs provider legalName, noticeAddress, and contact');
  const template=require('./approved_clauses.js');
  if(!contract.clauses || typeof contract.clauses!=='object') throw new Error('Contract profile needs a complete clauses object');
  for(const [key,value] of Object.entries(template)) {
    const actual=contract.clauses[key];
    if(Array.isArray(value) ? !Array.isArray(actual) || !actual.length : typeof actual!=='string' || !actual.trim())
      throw new Error('Missing or invalid contract clause: '+key);
  }
  if(!Number.isFinite(contract.upfrontPercent)||contract.upfrontPercent<0||contract.upfrontPercent>100)
    throw new Error('Contract profile upfrontPercent must be between 0 and 100');
  if(!['tm','fixed'].includes(model.pricingModel)) throw new Error('Quote must explicitly state pricingModel: tm or fixed');
  if(['assess','assessment','loe'].includes(variant) && model.pricingModel!=='fixed')
    throw new Error('Assessment and engagement-letter variants require a fixed-fee quote');
  if(!model.source?.reference) throw new Error('Quote needs source.reference');
  if(!model.timeline || !Array.isArray(model.timeline.bands) || model.timeline.bands.length!==1)
    throw new Error('Select exactly one quote band per SOW');
  if(!model.projectContext?.accountName || !model.projectContext?.quoteName || !model.projectSummary)
    throw new Error('Quote needs projectContext identity and projectSummary');
  if(!Array.isArray(model.scopeItemsByCapability)||!model.scopeItemsByCapability.length)
    throw new Error('Quote needs scopeItemsByCapability');
  const band=model.timeline.bands[0];
  if(!Array.isArray(band.resources)||!band.resources.length||!Array.isArray(band.phases))
    throw new Error('Quote band needs resources and phases');
  const output=path.resolve(args['--output']);
  if(path.extname(output).toLowerCase()!=='.docx') throw new Error('Output must end in .docx');
  if(fs.existsSync(output)||fs.existsSync(output+'.build.json')) throw new Error('Output already exists; choose a new attempt path');
  const replace = value => {
    if(typeof value==='string') return value.replaceAll('{PROVIDER}',provider.legalName).replaceAll('{UPFRONT_PERCENT}',String(contract.upfrontPercent));
    if(Array.isArray(value)) return value.map(replace);
    if(value && typeof value==='object') return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,replace(v)]));
    return value;
  };
  return {model,variant,args,contract,provider,clauses:replace(contract.clauses),output,
    sources:{modelSha256:crypto.createHash('sha256').update(fs.readFileSync(modelPath)).digest('hex'),
      contractSha256:crypto.createHash('sha256').update(fs.readFileSync(contractPath)).digest('hex'),
      quoteReference:model.source.reference,contractSource:contract.source}};
}

function reconcile(model, variant) {
  const band=model.timeline.bands[0], summary=model.projectSummary;
  const errors=[], close=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<0.011;
  const date=value=>{
    if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value)) return NaN;
    const parsed=Date.parse(value+'T00:00:00Z');
    return Number.isFinite(parsed)&&new Date(parsed).toISOString().slice(0,10)===value?parsed:NaN;
  };
  const start=date(band.startDate),end=date(band.endDate);
  if(!Number.isFinite(start)||!Number.isFinite(end)||end<start) errors.push('Engagement dates must be valid ISO dates in chronological order');
  const expires=model.projectContext.returnBy;
  if(expires && (!Number.isFinite(date(expires))||date(expires)>start)) errors.push('Signature return-by date must be valid and no later than the engagement start');
  let hours=0,revenue=0,phaseHours=0;
  const phaseNames=new Set(band.phases.map(p=>p.name));
  if(!band.phases.length || phaseNames.size!==band.phases.length) errors.push('Quote must contain uniquely named delivery phases');
  for(const phase of band.phases) {
    if(typeof phase.name!=='string'||!phase.name.trim()||typeof phase.purpose!=='string'||!phase.purpose.trim())
      errors.push('Each phase needs a name and sourced purpose');
    if(!Array.isArray(phase.weekNumbers)||!phase.weekNumbers.length||phase.weekNumbers.some(w=>!Number.isInteger(w)||w<1||w>summary.durationWeeks))
      errors.push('Each phase needs week numbers within the engagement duration');
  }
  for(const [i,r] of band.resources.entries()) {
    for(const key of ['totalHours','totalRevenue','billRate'])
      if(typeof r[key]!=='number'||!Number.isFinite(r[key])||r[key]<0) errors.push(`Resource ${i}: invalid ${key}`);
    if(r.discountAmount!==undefined && (!Number.isFinite(r.discountAmount)||r.discountAmount<0||r.discountAmount>r.totalHours*r.billRate))
      errors.push(`Resource ${i}: invalid discountAmount`);
    hours+=r.totalHours; revenue+=r.totalRevenue;
    if(!close(r.totalHours*r.billRate-(r.discountAmount||0),r.totalRevenue)) errors.push(`Resource ${i}: hours × rate minus discount differs from revenue`);
    const allocations=Object.entries(r.hoursByPhase||{});
    if(allocations.some(([name,h])=>!phaseNames.has(name)||!Number.isFinite(h)||h<0)) errors.push(`Resource ${i}: invalid phase allocation`);
    const allocated=allocations.reduce((a,[,h])=>a+h,0);phaseHours+=allocated;
    if((allocations.length || ['waterfall','agile'].includes(variant))&&!close(allocated,r.totalHours)) errors.push(`Resource ${i}: phase hours differ from total hours`);
  }
  if(!close(hours,summary.totalHours)) errors.push('Total resource hours differ from summary hours');
  if(!close(revenue,summary.totalValue)) errors.push('Total resource revenue differs from summary value');
  if(hours<=0) errors.push('Total hours must be positive');
  const blended=Math.round(revenue/hours*100)/100;
  if(!close(blended,model.timeline.summary?.blendedRate)) errors.push('Blended rate differs from source summary');
  let count=0;const walk=n=>{count+=(n.scopeItems||[]).length;(n.children||[]).forEach(walk);};
  model.scopeItemsByCapability.forEach(walk);
  if(count!==summary.totalScopeItems) errors.push('Scope item count differs from summary');
  if(!Number.isFinite(summary.durationWeeks)||summary.durationWeeks<=0) errors.push('Duration must be positive');
  return {tie:errors.length===0,errors,bl:blended,lines:[`hours by role = ${hours}`,`hours by phase = ${phaseHours}`,
    `summary hours = ${summary.totalHours}`,`revenue by role = ${revenue}`,`summary value = ${summary.totalValue}`,
    `blended rate = ${blended}`,`THREE-WAY TIE = ${errors.length?'FAIL':'PASS'}`]};
}
module.exports={readInputs,reconcile};
