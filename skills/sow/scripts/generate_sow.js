/* sow: full-contract SOW generator.
 * Variants: waterfall (default), agile, assess. Selected by argv[3].
 * Renders EVERY template section from the quote model. Mines Exhibit A
 * volumetrics, Change-Order triggers, and consolidated assumptions from the
 * scope items' own assumption text. Never fabricates: a missing source is a
 * visible FLAG and a logged row. Reconciles the three-way tie before render. */
const fs=require("fs");
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,ImageRun,Footer,
  AlignmentType,LevelFormat,TabStopType,TabStopPosition,TableOfContents,HeadingLevel,
  BorderStyle,WidthType,ShadingType,VerticalAlign,PageNumber,PageBreak,Bookmark,InternalHyperlink}=require("docx");

const path=require("path");
const {readInputs,reconcile}=require("./input_contract");
let input;
try { input=readInputs(process.argv.slice(2)); } catch(error) { console.error(error.message); process.exit(2); }
const m=input.model, variant=input.variant, provider=input.provider;
const brand=require("./brand_runtime");
const NAVY=brand.bare.textPrimary,NAVY2=brand.bare.textPrimary,TEAL=brand.bare.teal,
  STEEL=brand.bare.textMuted,SAND=brand.bare.sand,OFF=brand.bare.offWhite;
const INK=brand.bare.textPrimary,BORDER=brand.bare.border,CLAY=brand.bare.textPrimary,
  FONT=brand.type.office||"Arial",WHITE=brand.bare.white;
let LOGO=null, logoType=null, logoSize=null;
if(brand.logo) {
  const specification=typeof brand.logo==="string"?{path:brand.logo}:brand.logo;
  LOGO=path.resolve(path.dirname(brand.tokensPath),specification.path||"");
  if(!fs.existsSync(LOGO)||!fs.statSync(LOGO).isFile()) throw new Error("Declared logo is missing: "+LOGO);
  logoType=path.extname(LOGO).slice(1).toLowerCase();if(logoType==="jpg")logoType="jpeg";
  if(!["png","jpeg","gif","bmp"].includes(logoType)) throw new Error("Word logo must be PNG, JPEG, GIF, or BMP");
  const dimensions=require("image-size");const size=(dimensions.imageSize||dimensions.default||dimensions)(fs.readFileSync(LOGO));
  const scale=Math.min(168/size.width,48/size.height);logoSize={width:size.width*scale,height:size.height*scale};
}
const CW=9360;
const band=m.timeline.bands[0],ctx=m.projectContext,sum=m.projectSummary;
const log=[],flags=[],draftIssues=[];let delivCount=0;
const isAgile=variant==="agile",isAssess=variant==="assess"||variant==="assessment",isLoe=variant==="loe";
const ROLEMAP={"Solution SME":"Owns the assessment's point of view, leads the working sessions, and authors the findings and recommendation.","Solution Architect":"Owns the solution design and the technical decisions you sign off on.","Technical Architect":"Owns the integration and platform-technical design.","Business Analyst":"Translates your requirements into the documented design and backlog.","Sr Business Analyst":"Translates your requirements into the documented design and backlog.","Developer":"Builds and configures the solution to the approved design.","Program Manager":"Your single point of contact for status, risks, and change requests.","Project Manager":"Your single point of contact for status, risks, and change requests.","Client Services Executive":"Executive sponsor and escalation point for the engagement.","Quality Assurance":"Validates the build against the agreed acceptance criteria.","Quality Assurance (Nearshore)":"Validates the build against the agreed acceptance criteria."};
// Preserve role names from the selected quote. Only explicit aliases may rename them.
const ROLE_ALIAS=m.roleAliases||{};
const roleName=r=>ROLE_ALIAS[r]||r;

const T=(t,o={})=>new TextRun({text:String(t).replaceAll("{PROVIDER}",provider.legalName),font:FONT,...o});
const P=(runs,o={})=>new Paragraph({spacing:{before:80,after:120,line:276},children:runs,...o});
const anchor=t=>"section_"+t.replace(/[^a-zA-Z0-9]+/g,"_");
const h1=(t,o={})=>new Paragraph({...o,heading:HeadingLevel.HEADING_1,children:[new Bookmark({id:anchor(t),children:[T(t)]})]});
const h2=t=>new Paragraph({heading:HeadingLevel.HEADING_2,children:[T(t)]});
const h3=t=>new Paragraph({heading:HeadingLevel.HEADING_3,children:[T(t)]});
const h4=t=>new Paragraph({heading:HeadingLevel.HEADING_4,children:[T(t)]});
const bull=runs=>new Paragraph({numbering:{reference:"bullets",level:0},spacing:{after:60,line:264},children:runs});
const num=runs=>new Paragraph({numbering:{reference:"nums",level:0},spacing:{after:60,line:264},children:runs});
const flag=(t)=>{draftIssues.push(t);return T("[FLAG: "+t+"]",{size:22,bold:true,color:CLAY});};
function eng(val,section,name,source){if(val===null||val===undefined||val===""){log.push([section,name,"FLAGGED, not on quote",source,true]);return flag(name+" missing");}
  log.push([section,name,String(val),source,false]);return T(String(val),{size:22,color:INK});}
function reason(val,section,name,decision,source){if(val===null||val===undefined||val===""){log.push([section,name,"FLAGGED, source absent, not invented",source,true]);return flag(name+": "+decision);}
  log.push([section,name,String(val),source,false]);return T(String(val),{size:22,color:INK});}

// approved contractual language, verbatim, never paraphrased (see references/required-clauses.md)
const AC=input.clauses;
function clz(str,subs={}){return str.split(/(\{[A-Z_]+\})/).filter(s=>s!=="").map(p=>{const k=/^\{([A-Z_]+)\}$/.exec(p);if(k&&subs[k[1]]!==undefined){const v=subs[k[1]];return typeof v==="string"?T(v,{size:22,color:INK}):v;}return T(p,{size:22,color:INK});});}
const clzP=(str,subs,o)=>P(clz(str,subs),o);
// Render scope-item description/assumptions HTML into Word structure: <p> -> paragraph, <li> -> bullet.
function stripHtml(s){return (s||"").replace(/<\/(p|li|ul|ol|h[1-6])>/gi," ").replace(/<[^>]+>/g,"").replace(/&amp;/g,"&").replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&#39;|&apos;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g," ").trim();}
function htmlBlocks(s){if(!s)return [];const out=[];const re=/<(p|li)[^>]*>([\s\S]*?)<\/\1>/gi;let m,found=false;while((m=re.exec(s))){found=true;const t=stripHtml(m[2]);if(t)out.push({type:m[1].toLowerCase(),text:t});}if(found)return out;
  // No HTML block tags: treat as markdown/plain text. Split on newlines; "- ", "* ", "• " lines become bullets.
  String(s).split(/\r?\n/).forEach(line=>{const t=stripHtml(line);if(!t)return;const b=/^[-*•]\s+(.*)$/.exec(t);if(b)out.push({type:"li",text:b[1].trim()});else out.push({type:"p",text:t});});
  return out;}

const bd={style:BorderStyle.SINGLE,size:Math.max(1,Math.round(brand.rules.borderWidthPx*6)),color:BORDER},brd={top:bd,bottom:bd,left:bd,right:bd};
function cell(ch,{w,fill,head}={}){return new TableCell({borders:brd,width:{size:w,type:WidthType.DXA},verticalAlign:VerticalAlign.CENTER,
  shading:fill?{fill,type:ShadingType.CLEAR}:undefined,margins:{top:60,bottom:60,left:120,right:120},
  children:[new Paragraph({children:Array.isArray(ch)?ch:[T(String(ch),{size:20,color:head?WHITE:INK,bold:!!head})]})]});}
function table(widths,rows){return new Table({width:{size:CW,type:WidthType.DXA},columnWidths:widths,
  rows:rows.map((r,i)=>new TableRow({tableHeader:i===0,cantSplit:true,children:r.map((c,j)=>cell(c,{w:widths[j],fill:i===0?NAVY:(i%2?OFF:WHITE),head:i===0}))}))});}
const hd=t=>[T(t,{size:18,bold:true,color:WHITE})];
const money=n=>"$"+n.toLocaleString("en-US");
const sentences=s=>(s||"").split(/\.\s+/).map(x=>x.trim().replace(/\.$/,"")).filter(Boolean);
// Assess deliverable format, inferred from the deliverable's own name (si.format overrides). A "report"
// is a PDF, a "scorecard/register/matrix" is a spreadsheet, a "readout" is a deck. Contextual, not a fact.
const assessFormat=(name)=>{const n=(name||"").toLowerCase();
  if(/readout|deck|presentation|briefing|slides?/.test(n))return "PPTX";
  if(/scorecard|matrix|register|heatmap|inventory|mapping|scoring|appraisal|overlay|schema|worksheet|\btable\b/.test(n))return "XLSX";
  return "PDF";};

// Reconcile every resource before creating a document; offsetting errors must not cancel.
const rec=reconcile(m,variant);
if(!rec.tie) {
  fs.mkdirSync(path.dirname(input.output),{recursive:true});
  fs.writeFileSync(input.output+".build.json",JSON.stringify({state:"not-built",errors:rec.errors,...input.sources},null,2));
  console.error(rec.errors.join("\n"));process.exit(2);
}

// flatten scope tree (unwrap single phase/uncategorized wrapper)
let roots=m.scopeItemsByCapability;
if(roots.length===1&&roots[0].children?.length&&(roots[0].scopeItems?.length||0)===0){
  const wrap=roots[0].name;roots=roots[0].children;
  log.push(["Section 2.2","capability root","unwrapped '"+wrap+"' container → "+roots.length+" L1 capabilities","scopeItemsByCapability wrapper",true]);}
const items=[];
(function walk(node,path){const p=node.name?[...path,node.name]:path;
  (node.scopeItems||[]).forEach(si=>items.push({...si,capPath:p}));
  (node.children||[]).forEach(ch=>walk(ch,p));})({children:roots},[]);

// derived sections from assumptions
const QTY=/\b(up to|approximately|no more than)\b|\bone (integration|endpoint|connector)\b/i;
const CO=/change order|tier 3|tier-3/i;
const exhibitA=[],coTriggers=[];
items.forEach(si=>{sentences(stripHtml(si.assumptions)).forEach(s=>{
  if(QTY.test(s))exhibitA.push({item:si.name,text:s});
  if(CO.test(s))coTriggers.push({item:si.name,text:s});});});

const doc=new Document({creator:provider.legalName,title:`SOW ${ctx.quoteName}`,
  styles:{default:{document:{run:{font:FONT,size:22,color:INK}}},paragraphStyles:[
    {id:"Title",name:"Title",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:56,bold:true,font:FONT,color:NAVY},paragraph:{spacing:{before:120,after:120}}},
    {id:"Heading1",name:"Heading 1",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:32,bold:true,font:FONT,color:NAVY},paragraph:{spacing:{before:320,after:160},outlineLevel:0,keepNext:true}},
    {id:"Heading2",name:"Heading 2",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:26,bold:true,font:FONT,color:NAVY},paragraph:{spacing:{before:220,after:120},outlineLevel:1,keepNext:true}},
    {id:"Heading3",name:"Heading 3",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:22,bold:true,font:FONT,color:NAVY2},paragraph:{spacing:{before:160,after:80},outlineLevel:2,keepNext:true}},
    {id:"Heading4",name:"Heading 4",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:21,bold:true,font:FONT,color:TEAL},paragraph:{spacing:{before:120,after:60},outlineLevel:3,keepNext:true}}]},
  numbering:{config:[
    {reference:"bullets",levels:[{level:0,format:LevelFormat.BULLET,text:"•",alignment:AlignmentType.LEFT,style:{run:{color:TEAL},paragraph:{indent:{left:460,hanging:260}}}}]},
    {reference:"nums",levels:[{level:0,format:LevelFormat.DECIMAL,text:"%1.",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:520,hanging:320}}}}]}]},
  sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1440,right:1440,bottom:1440,left:1440}}},
    footers:{default:new Footer({children:[new Paragraph({tabStops:[{type:TabStopType.RIGHT,position:TabStopPosition.MAX}],
      children:[T("CONFIDENTIAL",{size:16,color:STEEL}),new TextRun({children:["\tPage ",PageNumber.CURRENT," of ",PageNumber.TOTAL_PAGES],font:FONT,size:16,color:STEEL})]})]})},
    children:build()}]});

function scopeNodes(){const out=[];
  (function walk(node,depth){if(node.name){if(depth===1)out.push(h3(node.name));else if(depth>=2)out.push(h4(node.name));}
    (node.scopeItems||[]).forEach(si=>{
      out.push(P([T((si.name||"Scope")+".",{size:22,bold:true,color:NAVY2})],{keepNext:true}));
      if(!si.description){out.push(P([flag("scope description MISSING: return to scoping-agent")]));flags.push([node.name+" › "+si.name,"description MISSING","scoping-agent"]);}
      else htmlBlocks(si.description).forEach(b=> b.type==="li" ? out.push(bull([T(b.text,{size:22,color:INK})])) : out.push(P([T(b.text,{size:22,color:INK})])) );
      if(!si.assumptions)flags.push([node.name+" › "+si.name,"assumptions MISSING","add or confirm none"]);});
    (node.children||[]).forEach(ch=>walk(ch,depth+1));})({children:roots},0);
  return out;}

function build(){const c=[];
  if(input.contract.status==="example")c.push(P([T("Synthetic example for skill testing",{bold:true})]));
  if(input.args["--draft"])c.push(P([T("Working draft with unresolved inputs",{bold:true})]));
  if(isLoe)return buildLetter();
  // cover
  if(LOGO)c.push(new Paragraph({spacing:{after:200},children:[new ImageRun({type:logoType,data:fs.readFileSync(LOGO),transformation:logoSize,altText:{title:provider.legalName,description:"logo",name:"logo"}})]}));
  c.push(new Paragraph({style:"Title",spacing:{before:120,after:60},children:[T("Statement of Work")]}));
  c.push(new Paragraph({spacing:{after:40},children:[T(isAssess?"Assessment engagement":isAgile?"Adaptive delivery (Agile) engagement":"Phase-gated waterfall engagement",{size:24,color:TEAL})]}));
  c.push(P([T("Prepared for  ",{size:22,color:STEEL}),eng(ctx.accountName,"Cover","accountName","projectContext.accountName"),T("   •   Prepared by  ",{size:22,color:STEEL}),T(provider.legalName,{size:22,color:INK})]));
  c.push(P([T("Engagement  ",{size:22,color:STEEL}),eng(ctx.opportunityName,"Cover","projectName","projectContext.opportunityName"),T("   •   Quote  ",{size:22,color:STEEL}),eng(ctx.quoteName,"Cover","quoteName","projectContext.quoteName")]));
  if(isAssess){
    // Fixed-fee cover: investment and duration only. No total-hours or blended-rate columns; those read
    // as T&M economics on a fixed-fee engagement and invite hour and rate disputes.
    c.push(table([4680,4680],[[hd("Investment"),hd("Duration")],
      [[eng(money(sum.totalValue),"Cover","totalInvestment","projectSummary.totalValue"),T("  (fixed fee)",{size:20,color:STEEL})],[eng(sum.durationWeeks,"Cover","durationWeeks","projectSummary.durationWeeks"),T(" weeks",{size:22,color:INK})]]]));
  } else {
  c.push(table([2340,2340,2340,2340],[hd("Investment").length?[hd("Investment"),hd("Duration"),hd("Total hours"),hd("Blended rate")]:[],
    [[eng(money(sum.totalValue),"Cover","totalInvestment","projectSummary.totalValue")],[eng(sum.durationWeeks,"Cover","durationWeeks","projectSummary.durationWeeks"),T(" weeks",{size:22,color:INK})],[eng(sum.totalHours,"Cover","totalHours","projectSummary.totalHours")],[eng("$"+rec.bl,"Cover","blendedRate","timeline.summary.blendedRate"),T("/hr",{size:22,color:INK})]]]));
  }
  c.push(h2("Parties and notice"));
  const clientName=ctx.accountName||null;
  log.push(["Parties","clientLegalName",clientName||"FLAGGED, not on quote","projectContext.accountName",!clientName]);
  c.push(clzP(AC.PREAMBLE,{CLIENT:clientName||"[CLIENT LEGAL NAME, confirm]"}));
  c.push(P([T("Effective Date:  ",{size:22,bold:true,color:INK}),T("____________   ",{size:22,color:INK}),T("(completed when signed)",{size:18,italics:true,color:STEEL})]));
  c.push(P([T("Professional Services Agreement Effective Date:  ",{size:22,bold:true,color:INK}),reason(ctx.psaEffectiveDate,"Cover","PSA effective date","blank if SOW001; else original PSA date","not in quote")]));
  c.push(table([4680,4680],[[hd(AC.NOTICE_SP_LABEL),hd(AC.NOTICE_CLIENT_LABEL)],
    [[T(provider.legalName,{size:22,bold:true,color:INK}),...provider.noticeAddress.map(line=>new TextRun({break:1,text:line,font:FONT,size:22,color:INK})),new TextRun({break:2,text:"Attn: "+provider.contact,font:FONT,size:22,color:INK})],
     [eng(ctx.accountName,"Parties","clientLegalName","projectContext.accountName"),new TextRun({break:1}),reason(ctx.clientAddress,"Parties","client address","confirm address","not in quote"),new TextRun({break:2,text:"Attn: ",font:FONT,size:22,color:INK}),reason(ctx.clientContact,"Parties","client contact","confirm name, title","not in quote")]]]));
  c.push(new Paragraph({children:[new PageBreak()]}));
  c.push(h1("Contents"));
  const contents=["1. Engagement overview","2. Scope","3. Delivery methodology","4. Deliverables",
    "5. Timeline and engagement structure","6. Service Provider team and roles","7. Client responsibilities and assumptions",
    "8. Change control","9. Investment",isAssess?"10. Acceptance":"10. Acceptance and defect resolution",
    "11. Miscellaneous terms","Acceptance and signatures",...(!isAssess?["Exhibit A. Basis of estimate"]:[]),
    ...(isAssess&&m.instruments?.length?["Appendix A. Assessment instruments and methods"]:[])];
  contents.forEach(title=>c.push(P([new InternalHyperlink({anchor:anchor(title),children:[T(title,{color:INK})]})])));
  c.push(new Paragraph({children:[new PageBreak()]}));
  // 1
  c.push(h1("1. Engagement overview"));c.push(h2("1.1 Purpose"));
  const ctxL1=roots.map(r=>r.name).filter(Boolean);
  const ctxPlatform=m.platform||m.targetPlatform||(ctxL1.some(n=>/rca|revenue cloud/i.test(n))?"Salesforce Revenue Cloud Advanced (RCA)":null);
  // Section 1.1 Purpose. Prefer a sourced narrative (businessNeed) or one inferred at invocation (purposeNarrative); else build a grounded
  // inference from quote signals, never a bare flag. Inferred values are logged for confirmation (contextual framing, not invented facts).
  if(ctx.businessNeed){c.push(P([T(String(ctx.businessNeed),{size:22,color:INK})]));log.push(["Section 1.1","purpose narrative",String(ctx.businessNeed),"projectContext.businessNeed",false]);}
  else if(m.purposeNarrative){c.push(P([T(String(m.purposeNarrative),{size:22,color:INK})]));log.push(["Section 1.1","purpose narrative","model-supplied, inferred at invocation, confirm","model.purposeNarrative",true]);}
  else{
    const acct=ctx.accountName||"The Client";
    const opp=ctx.opportunityName?(" for "+ctx.opportunityName):"";
    const areas=ctxL1.length?(" across "+ctxL1.length+" capability "+(ctxL1.length===1?"area":"areas")+" ("+ctxL1.join(", ")+")"):"";
    const plat=ctxPlatform?(" on "+ctxPlatform):"";
    const inferred=acct+" has engaged Service Provider"+opp+". Service Provider will deliver "+sum.totalScopeItems+" scope items"+areas+plat+" over "+sum.durationWeeks+" weeks, within the scope and boundary defined in Section 2.";
    c.push(P([T(inferred,{size:22,color:INK})]));
    log.push(["Section 1.1","purpose narrative","INFERRED from quote signals (opportunity, capabilities, platform, duration), confirm","reasoned from quote; businessNeed null",true]);
  }
  c.push(h2("1.2 Engagement context"));
  // Structured context table. Deterministic fields filled from the model; narrative fields inferred from available signals (logged for confirmation); contact fields flagged.
  const cxRow=(label,runs)=>[[T(label,{size:20,bold:true,color:INK})],runs];
  let driverRun;
  if(ctx.businessDriver){driverRun=T(String(ctx.businessDriver),{size:20,color:INK});log.push(["§1.2","engagement driver",String(ctx.businessDriver),"projectContext.businessDriver",false]);}
  else if(m.engagementDriver){driverRun=T(String(m.engagementDriver),{size:20,color:INK});log.push(["§1.2","engagement driver","model-supplied, inferred at invocation — confirm","model.engagementDriver",true]);}
  else if(m.engagementType){driverRun=T(String(m.engagementType),{size:20,color:INK});log.push(["§1.2","engagement driver","INFERRED from engagement type — confirm","model.engagementType",true]);}
  else if(ctxPlatform){driverRun=T("Migration to "+ctxPlatform+".",{size:20,color:INK});log.push(["§1.2","engagement driver","INFERRED from target platform — confirm","detected platform",true]);}
  else{driverRun=reason(null,"§1.2","engagement driver","from businessDriver","projectContext.businessDriver");}
  const cxCommon=[
    cxRow("Client legal entity",[ctx.accountName?T(ctx.accountName,{size:20,color:INK}):flag("client legal entity: confirm")]),
    cxRow("Primary contact",[reason(ctx.primaryContact,"Context","primary contact","name, title, email","projectContext.primaryContact")]),
    cxRow("Executive sponsor",[reason(ctx.executiveSponsor,"Context","executive sponsor","name, title","projectContext.executiveSponsor")]),
    cxRow("Provider engagement lead",[reason(ctx.providerLead,"Context","provider lead","name, title","projectContext.providerLead")]),
    cxRow("Engagement type",[m.engagementType?T(m.engagementType,{size:20,color:INK}):reason(null,"§1.2","engagement type","name the migration or build type","not in quote")]),
  ];
  // Assess context omits Target platform / Source system: those are build fields, and on a directional
  // assessment the platform is often the thing the engagement exists to choose. Pricing model stated instead.
  const cxAssess=[...cxCommon,
    cxRow("Pricing model",[T("Fixed fee",{size:20,color:INK})]),
    cxRow("Engagement driver",[driverRun]),
  ];
  const cxBuild=[...cxCommon,
    cxRow("Target platform",[ctxPlatform?T(ctxPlatform,{size:20,color:INK}):reason(null,"§1.2","target platform","infer from in-scope capabilities","no platform capability detected")]),
    cxRow("Source system",[m.sourceSystem?T(m.sourceSystem,{size:20,color:INK}):flag("source system: confirm")]),
    cxRow("Engagement driver",[driverRun]),
  ];
  c.push(table([3000,6360],[[hd("Field"),hd("Details")],...(isAssess?cxAssess:cxBuild)]));
  log.push(["§1.2","engagement context","structured table rendered (deterministic fields filled, others flagged)","projectContext + model overrides",false]);
  // 2
  c.push(h1("2. Scope"));c.push(h2("2.1 Scope summary and boundary"));
  c.push(clzP(AC.PROJECT_SCOPE_INTRO));
  c.push(P([T("This SOW covers ",{size:22,color:INK}),eng(sum.totalScopeItems,"Section 2.1","totalScopeItems","projectSummary.totalScopeItems"),T(" scope items across ",{size:22,color:INK}),eng(roots.length,"Section 2.1","capabilityCount","count of L1 nodes"),T((roots.length===1?" capability area.":" capability areas.")+" Work not described here is out of scope and handled through Change Control (Section 8).",{size:22,color:INK})]));
  // Engagement boundary paragraph (model-supplied) + attribute summary table. Duration/Investment deterministic; type/boundary flagged when absent.
  if(m.engagementBoundary)c.push(P([T(m.engagementBoundary,{size:22,color:INK})]));
  const pmLabel=((m.pricingModel).toLowerCase()==="tm")?"Time & Materials estimate":"fixed fee";
  c.push(table([3000,6360],[[hd("Attribute"),hd("Summary")],
    [[T("Engagement type",{size:20,bold:true,color:INK})],[m.engagementType?T(m.engagementType,{size:20,color:INK}):reason(null,"Section 2.1","engagement type","name the migration or build type","not in quote")]],
    [[T("Duration",{size:20,bold:true,color:INK})],[T(sum.durationWeeks+" weeks",{size:20,color:INK})]],
    [[T("Investment",{size:20,bold:true,color:INK})],[T(money(sum.totalValue)+"  ("+pmLabel+")",{size:20,color:INK})]],
    [[T("Boundary",{size:20,bold:true,color:INK})],[m.boundarySummary?T(m.boundarySummary,{size:20,color:INK}):reason(null,"Section 2.1","boundary","one-line scope boundary","not in quote")]]]));
  log.push(["Section 2.1","attribute summary","engagement type/duration/investment/boundary table","projectSummary + model overrides",false]);
  c.push(h2("2.2 In-scope workstreams"));
  c.push(P([T("Section 7.2 lists the assumptions used to estimate this work.",{size:22,color:INK})]));scopeNodes().forEach(n=>c.push(n));
  c.push(h2("2.3 Explicit exclusions"));
  c.push(clzP(AC.OUT_OF_SCOPE_HEADER));
  if(Array.isArray(m.exclusions)&&m.exclusions.length){m.exclusions.forEach(x=>c.push(bull([T(x,{size:22,color:INK})])));log.push(["Section 2.3","exclusions",m.exclusions.length+" named exclusions rendered","model.exclusions",false]);}
  else c.push(bull([reason(null,"Section 2.3","exclusions","pull named exclusions; tag by reason","quote has none")]));
  c.push(clzP(AC.CATCH_ALL_EXCLUSION));
  // 3
  c.push(h1("3. Delivery methodology"));
  c.push(P([reason(m.deliveryMethodology,"Section 3","delivery methodology","confirm the delivery method","model.deliveryMethodology")]));
  c.push(table([2600,900,5860],[[hd(isAssess?"Stage":isAgile?"Stage / sprint":"Phase"),hd("Weeks"),hd("Delivery focus")],
    ...band.phases.map(p=>{log.push(["Section 3","phasePurpose:"+p.name,p.purpose||"FLAGGED null","phases[].purpose",!p.purpose]);
      return [[T(p.name,{size:20,color:INK})],[T(p.weeks,{size:20,color:INK})],[p.purpose?T(p.purpose,{size:20,color:INK}):flag("purpose missing")]];})]));
  if(isAssess)c.push(P([T("Stages organize the assessment work. Deliverable acceptance is defined in Section 10.",{size:20,color:STEEL})]));
  // 4
  c.push(h1("4. Deliverables"));
  c.push(P([T(isAssess?"The following deliverables are produced during the engagement and presented at the executive readout. The deliverable set below fixes the scope of the engagement; work beyond it is a Change Order.":"The table lists the deliverables and their formats. Section 10 defines how the Client reviews and accepts them.",{size:22,color:INK})]));
  const l1Areas=roots.map(r=>r.name);
  const platform=m.platform||(l1Areas.some(n=>/rca|revenue cloud/i.test(n))?"Salesforce Revenue Cloud Advanced":null);
  log.push(["Section 4","in-scope areas",l1Areas.join(", "),"L1 capabilities",false]);
  log.push(["Section 4","platform",platform||"FLAGGED, infer/confirm",platform?"RCA capability present":"no RCA capability",!platform]);
  const reqDesc=[T("Documented requirements across the in-scope capability areas ("+l1Areas.join(", ")+"), detailed in Section 2. Co-signed before design begins.",{size:20,color:INK})];
  const desDesc=[T("Design recommendations for delivering the in-scope requirements on ",{size:20,color:INK}),platform?T(platform,{size:20,color:INK}):flag("platform - confirm"),T(", including object model, to-be processes, automation approach, and data-migration field mapping. Co-signed before Build begins.",{size:20,color:INK})];
  const cfgName=platform?platform+" Configuration":"Platform Configuration";
  const cfgDesc=[T("Configured ",{size:20,color:INK}),platform?T(platform,{size:20,color:INK}):flag("platform - confirm"),T(" across the in-scope areas, including the in-scope custom development and the validated migration of in-scope records, deployed post system sign-off.",{size:20,color:INK})];
  const assessDeliv=items.map(si=>{
    return [[T(si.name,{size:20,color:INK})],
      [si.description?T(stripHtml(si.description),{size:20,color:INK}):flag(si.name+" description missing")],
      [T(si.format||assessFormat(si.name),{size:18,color:INK})]];});
  let delivRows=isAssess?assessDeliv:isAgile?[
    [[T("High-Level Solution Design",{size:20,color:INK})],[T("Architecture, object model, and integration design baseline across the in-scope areas ("+l1Areas.join(", ")+"); established in Plan and Architect.",{size:20,color:INK})],[T("Word / G Docs",{size:18,color:INK})]],
    [[T("Story Map and Product Backlog",{size:20,color:INK})],[T("Prioritized user stories with acceptance criteria, maintained through delivery.",{size:20,color:INK})],[T("Jira / G Sheets",{size:18,color:INK})]],
    [[T("Sprint Increments and Demos",{size:20,color:INK})],[T("Working, demonstrated increments delivered each sprint and accepted per Section 10.",{size:20,color:INK})],[T("Salesforce",{size:18,color:INK})]],
    [[T("QA and Test Plan",{size:20,color:INK})],[T("Test approach and results across unit, SIT, UAT, and regression.",{size:20,color:INK})],[T("Word / G Docs",{size:18,color:INK})]],
    [[T(cfgName,{size:20,color:INK})],cfgDesc,[T("Salesforce",{size:18,color:INK})]],
    [[T("Admin Training Guide",{size:20,color:INK})],[T("Admin training guide covering the delivered configuration, for the Client administrator.",{size:20,color:INK})],[T("PPT / G Slides",{size:18,color:INK})]]
  ]:[
    [[T("Requirements Doc",{size:20,color:INK})],reqDesc,[T("Excel / G Sheets",{size:18,color:INK})]],
    [[T("Solution Design Doc",{size:20,color:INK})],desDesc,[T("Word / G Docs",{size:18,color:INK})]],
    [[T("Training Doc",{size:20,color:INK})],[T("Admin training guide covering the migrated configuration, for the Client administrator.",{size:20,color:INK})],[T("PPT / G Slides",{size:18,color:INK})]],
    [[T(cfgName,{size:20,color:INK})],cfgDesc,[T("Salesforce",{size:18,color:INK})]]
  ];
  if(Array.isArray(m.deliverables)&&m.deliverables.length) {
    delivRows=m.deliverables.map(d=>[[T(d.name,{size:20,color:INK})],[T(d.description,{size:20,color:INK})],[T(d.format,{size:18,color:INK})]]);
  } else if(!isAssess) draftIssues.push("Confirm deliverables in model.deliverables; rendered rows are draft suggestions");
  delivCount=delivRows.length;
  c.push(table([2400,5160,1800],[[hd("Deliverable"),hd("Description"),hd("Format")],...delivRows]));
  if(isAssess && items.some(si=>!si.format) && !m.deliverables) draftIssues.push("Confirm assessment deliverable formats");
  if(!isAssess)c.push(P([reason(m.scopeNote,"Section 4","scope note","confirm which supporting activities are included","model.scopeNote")]));
  // 5
  c.push(h1("5. Timeline and engagement structure"));c.push(h2("5.1 Duration"));
  c.push(clzP(AC.ELAPSED_PERIOD,{N:String(sum.durationWeeks)}));
  c.push(clzP(isAssess?AC.COMMENCEMENT_STAFFING_ASSESS:AC.COMMENCEMENT_STAFFING));
  c.push(P([T("Estimated at ",{size:22,color:INK}),eng(sum.durationWeeks,"§5.1","durationWeeks","projectSummary.durationWeeks"),T(" weeks, beginning ",{size:22,color:INK}),eng(band.startDate,"§5.1","startDate","bands[].startDate"),T(" and concluding ",{size:22,color:INK}),eng(band.endDate,"§5.1","endDate","bands[].endDate"),T(".",{size:22,color:INK})]));
  c.push(h2("5.2 Role engagement"));
  if(isAssess){
    c.push(P([T("The roles engaged on this assessment and their estimated hours. The fixed fee is in Section 9.",{size:22,color:INK})]));
    c.push(table([4680,2340,2340],[[hd("Role"),hd("Hours"),hd("Title level")],
      ...band.resources.map(r=>[[T(roleName(r.role),{size:20,color:INK})],[T(String(r.totalHours),{size:20,color:INK})],[T(r.titleLevel||"",{size:18,color:INK})]])]));
  } else {
  c.push(P([T("The table shows when each role participates. Section 3 describes the work in each "+(isAgile?"stage":"phase")+". Weekly hours are specified separately.",{size:22,color:INK})]));
  c.push(table([3400,5960],[[hd("Role"),hd(isAgile?"Active stages":"Active phases")],
    ...band.resources.map(r=>{const act=band.phases.filter(p=>(r.hoursByPhase[p.name]||0)>0).map(p=>p.name);return [[T(roleName(r.role),{size:20,color:INK})],[T(act.length?act.join(", "):"(none)",{size:20,color:INK})]];})]));
  }
  // 6
  c.push(h1("6. Service Provider team and roles"));
  c.push(P([T("The Service Provider team for this engagement and what each role owns. "+(isAssess?"The fixed fee is in Section 9.":"Hours and rates are in Section 9."),{size:22,color:INK})]));
  c.push(table([3400,5960],[[hd("Role"),hd("What they own")],
    ...band.resources.map(r=>{const rn=roleName(r.role);const own=r.responsibility;log.push(["Section 6","role: "+rn,own?"(client-facing responsibility rendered)":"FLAGGED, confirm responsibility","bands[].resources[].responsibility",!own]);return [[T(rn,{size:20,color:INK})],[own?T(own,{size:20,color:INK}):flag(rn+" responsibility: confirm")]];})]));
  c.push(clzP(isAssess?AC.PROJECT_MANAGEMENT_INTRO_ASSESS:AC.PROJECT_MANAGEMENT_INTRO));
  (isAssess?AC.PROJECT_MANAGEMENT_BULLETS_ASSESS:AC.PROJECT_MANAGEMENT_BULLETS).forEach(b=>c.push(bull([T(b,{size:22,color:INK})])));
  // 7
  c.push(h1("7. Client responsibilities and assumptions"));c.push(h2("7.1 Client responsibilities"));
  c.push(clzP(AC.CLIENT_RELIANCE));
  c.push(clzP(isAssess?AC.CLIENT_RESOURCES_INTRO_ASSESS:AC.CLIENT_RESOURCES_INTRO));
  const clientRoles=isAssess?AC.CLIENT_RESOURCES_ASSESS:AC.CLIENT_RESOURCES;
  const clientNote=isAssess?AC.CLIENT_RESOURCES_NOTE_ASSESS:AC.CLIENT_RESOURCES_NOTE;
  c.push(table([2600,5160,1600],[[hd("Role"),hd("Responsibility"),hd("Expected time commitment")],
    ...clientRoles.map(r=>[[T(r.role,{size:20,bold:true,color:INK})],[T(r.responsibility,{size:20,color:INK})],[T(r.commitment,{size:18,color:INK})]])]));
  c.push(P([T(clientNote,{size:18,italics:true,color:STEEL})]));
  log.push(["Section 7.1","client responsibilities",clientRoles.length+(isAssess?" assessment":" build")+" client roles rendered",isAssess?"approved_clauses.CLIENT_RESOURCES_ASSESS":"approved_clauses.CLIENT_RESOURCES",false]);
  c.push(h2("7.2 Key assumptions"));
  c.push(P([T("The estimate depends on the assumptions below. If an assumption changes, use Change Control to agree any change to effort, schedule or fees.",{size:22,color:INK})]));
  // Section 7.2 states the load-bearing CONDITION only. The Change-Order consequence is owned once by Section 8.1
  // (and by the Section 7.2 intro above), do not restate "triggers a Change Order" on every line.
  let a=0;items.forEach(si=>{if(!si.assumptions)return;a++;
    const assumPlain=stripHtml(si.assumptions);
    const cond=sentences(assumPlain).filter(s=>!CO.test(s)).join(". ");
    const a72=cond?cond+".":assumPlain;
    c.push(num([T("A-"+String(a).padStart(2,"0")+"  ",{size:22,bold:true,color:NAVY2}),T(si.name+": ",{size:22,bold:true,color:INK}),T(a72,{size:22,color:INK})]));});
  log.push(["Section 7.2","consolidated assumptions",a+" load-bearing assumptions rendered","scope item assumptions",false]);
  c.push(h2("7.3 Protective clauses"));
  // For assess, drop two build-shaped protective clauses: AppExchange selection (already excluded) and the
  // "workshops to define business processes and requirements" clause (requirements-gathering language). The
  // gated change-order clause (#13, "a Change Order will be mutually agreed upon and executed") is a separate
  // string and stays, so the gate is unaffected.
  const APPEXCHANGE=/AppExchange/i;const WORKSHOP=/Additional time to conduct workshops/i;
  AC.PROTECTIVE_ASSUMPTIONS.filter(t=>!(isAssess&&(APPEXCHANGE.test(t)||WORKSHOP.test(t)))).forEach(t=>c.push(bull([T(t,{size:22,color:INK})])));
  c.push(clzP(AC.LOCATION_OF_SERVICES));
  log.push(["Section 7.3","protective clauses",AC.PROTECTIVE_ASSUMPTIONS.length+" approved clauses + Location of Services, rendered verbatim","approved_clauses.js (legally approved template)",false]);
  // 8
  c.push(h1("8. Change control"));c.push(h2("8.1 Change order triggers"));
  const curatedCO=Array.isArray(m.changeOrderTriggers)&&m.changeOrderTriggers.length?m.changeOrderTriggers:null;
  c.push(P([T(isAssess?"Scope is fixed by the deliverable list in Section 4. The following, drawn from the scope assumptions, trigger a Change Order:":isAgile?"Backlog reprioritization within the agreed sprint capacity is managed by the team and is not a Change Order. The following, drawn from the scope assumptions, trigger a Change Order:":"Scope is fixed at SOW execution. The following, drawn from the scope assumptions, trigger a Change Order:",{size:22,color:INK})]));
  if(curatedCO)curatedCO.forEach(t=>c.push(bull([T(t,{size:22,color:INK})])));
  else if(coTriggers.length)coTriggers.forEach(t=>c.push(bull([T(t.text+" ",{size:22,color:INK}),T("("+t.item+")",{size:18,italics:true,color:STEEL})])));
  else c.push(bull([flag("no Change-Order triggers found in assumptions: review")]));
  log.push(["Section 8.1","change-order triggers",curatedCO?curatedCO.length+" curated categorical triggers":coTriggers.length+" mined from assumptions","model.changeOrderTriggers || scope assumptions",!curatedCO&&coTriggers.length===0]);
  c.push(h2("8.2 Process"));
  c.push(P([T(isAgile?"Change Orders are agreed in good faith and documented before the affected work is committed to a sprint. Change-order work bills at list rate.":"Change Orders are agreed in good faith and documented before work begins. No work is performed in anticipation of approval. Change-order work bills at list rate.",{size:22,color:INK})]));
  // 9
  c.push(h1("9. Investment"));c.push(h2("9.1 Professional arrangements"));
  // model.json carries no pricing-model field, default Time & Materials and FLAG for human confirmation.
  const PRICING_MODEL=m.pricingModel;
  const upfront=money(Math.round(sum.totalValue*input.contract.upfrontPercent)/100);
  log.push(["Section 9.1","pricing model",isAssess?"Fixed fee (assessment)":PRICING_MODEL==="tm"?"Time & Materials (DEFAULT)":"Fixed fee",isAssess?"assess variant, assessments are fixed price":m.pricingModel?"model.pricingModel":"DEFAULT, no pricing field on quote; confirm with Deal Desk",isAssess?false:!m.pricingModel]);
  c.push(P(isAssess?[T("This assessment is delivered for a fixed fee of ",{size:22,color:INK}),eng(money(sum.totalValue),"Section 9.1","totalInvestment","projectSummary.totalValue"),T(", covering the deliverables in Section 4.",{size:22,color:INK})]:[T("Hours drive the fee. Total professional fees are ",{size:22,color:INK}),eng(money(sum.totalValue),"Section 9.1","totalInvestment","projectSummary.totalValue"),T(" for ",{size:22,color:INK}),eng(sum.totalHours,"Section 9.1","totalHours","projectSummary.totalHours"),T(" hours.",{size:22,color:INK})]));
  c.push(clzP(PRICING_MODEL==="tm"?AC.TM_CLOSE:AC.FIXED_CLOSE,{TOTAL:money(sum.totalValue)}));
  if(isAssess){
    // Fixed fee: state hours once as an estimate and fix the fee to them. No per-role rate table: a fixed
    // fee is not an hours×rate computation, and an evenly-plugged blended rate on every role reads as
    // reverse-engineered and invites unused-hour and rate disputes.
    c.push(P([T("Estimated at ",{size:22,color:INK}),eng(sum.totalHours,"§9.1","totalHours","projectSummary.totalHours"),T(" hours across the team. The fee is fixed regardless of actual hours.",{size:22,color:INK})]));
    log.push(["§9","fees-by-role rate table","omitted for assess (fixed fee is not hours×rate)","assess variant",false]);
  } else {
  c.push(h2("9.2 Fees by role"));
  c.push(table([3400,1600,1600,2760],[[hd("Role"),hd("Rate"),hd("Hours"),hd("Fee")],
    ...band.resources.map(r=>[[T(roleName(r.role),{size:20,color:INK})],[T("$"+r.billRate,{size:20,color:INK})],[T(String(r.totalHours),{size:20,color:INK})],[T(money(r.totalRevenue),{size:20,color:INK})]]),
    [[T("Total",{size:20,bold:true,color:INK})],[T("",{})],[T(String(sum.totalHours),{size:20,bold:true,color:INK})],[T(money(sum.totalValue),{size:20,bold:true,color:INK})]]]));
  c.push(h2("9.3 Summary"));
  c.push(P([T(`Blended rate $${rec.bl}/hr across a team of `,{size:22,color:INK}),eng(sum.teamSize,"§9.3","teamSize","projectSummary.teamSize"),T(` over ${sum.durationWeeks} weeks.`,{size:22,color:INK})]));
  }
  c.push(h2(isAssess?"9.2 Payment terms":"9.4 Payment terms"));
  c.push(clzP(PRICING_MODEL==="tm"?AC.TM_UPFRONT:AC.FIXED_INVOICES,{UPFRONT:upfront}));
  c.push(clzP(AC.EXPENSES_CARVEOUT));
  c.push(P([T(AC.REMITTANCE_BILLTO_LABEL,{size:22,color:INK})],{keepNext:true}));
  c.push(P([eng(ctx.accountName,"Section 9.4","client A/P recipient","projectContext.accountName"),new TextRun({break:1}),reason(ctx.accountsPayable,"Section 9.4","client A/P address & email","confirm accounts-payable address and email","not in quote")]));
  c.push(P([T(AC.REMITTANCE_PAY_LABEL,{size:22,color:INK})],{keepNext:true}));
  // Stacked layout: label on its own line, each detail line on its own line (matches the live SOWs).
  const stacked=(label,lines)=>P([T(label,{size:22,bold:true,color:INK}),...lines.flatMap(l=>[new TextRun({break:1}),T(l,{size:22,color:INK})])]);
  c.push(stacked("Payment by Check:",AC.REMITTANCE_CHECK));
  c.push(stacked("All Electronic Payments:",AC.REMITTANCE_ELECTRONIC));
  // 10
  if(isAssess){
    c.push(h1("10. Acceptance"));
    c.push(P([T("The Client reviews the findings and recommendations in Section 4 at the final presentation. The acceptance terms below apply to those deliverables.",{size:22,color:INK})]));
    c.push(clzP(AC.DEEMED_ACCEPTANCE));
    c.push(P([T("Because the engagement produces findings and recommendations rather than software, a non-conformance is limited to a factual error in a deliverable, which Service Provider will correct within the review period. The review period is not a mechanism to expand scope or to reopen the recommendation.",{size:22,color:INK})]));
    log.push(["§10","acceptance model","single model: deemed acceptance (clause #12) with the readout as the delivery event","assess variant",false]);
  } else {
  c.push(h1("10. Acceptance and defect resolution"));c.push(h2("10.1 Defect severity"));
  c.push(P([T(AC.DEFECT_SEVERITY_INTRO,{size:22,color:INK})]));
  c.push(P([T(AC.DEFECT_GONOGO,{size:22,color:INK})]));
  c.push(table([1800,7560],[[hd("Severity"),hd("Definition and resolution commitment")],
    [[T("Severity 1",{size:20,bold:true,color:INK})],"Critical: blocks go-live. Resolved before Go/No-Go."],
    [[T("Severity 2",{size:20,bold:true,color:INK})],"Major: significant impact, workaround exists."],
    [[T("Severity 3",{size:20,bold:true,color:INK})],"Minor: limited impact."],
    [[T("Severity 4",{size:20,bold:true,color:INK})],"Trivial: cosmetic."]]));
  c.push(h2("10.2 Deliverable acceptance"));
  c.push(clzP(AC.DEEMED_ACCEPTANCE));
  c.push(P([T("The Client must accept the user testing results before production deployment.",{size:22,color:INK})]));
  // validate-period resolved deterministically from the Validate phase
  const vp=band.phases.find(p=>p.name==="Validate");
  const vw=(vp&&Array.isArray(vp.weekNumbers))?vp.weekNumbers.length:null;const numWord=["zero","one (1)","two (2)","three (3)","four (4)","five (5)"][vw]||(vw+"");
  c.push(P([T(isAgile?"The Client will provide a Product Owner and UAT resources throughout delivery, with focused acceptance over the ":"The Client will provide adequate resources for UAT over a ",{size:22,color:INK}),
    (vp&&vw)?(()=>{log.push(["Section 10.2","validate-period duration",numWord+" week","Validate phase weekNumbers="+JSON.stringify(vp.weekNumbers),false]);return T(numWord+" week",{size:22,color:INK});})():flag("validate period, no Validate phase"),
    T(isAgile?" validation stage. ":" validate period. ",{size:22,color:INK}),
    T(isAgile?"Test scripts used during validation are ":"Test scripts used during the Validate phase are ",{size:22,color:INK}),reason(ctx.testScriptOwnership,"Section 10.2","test-script ownership","client- or Service Provider-created, from UAT-strategy assumption","no UAT-strategy assumption on quote"),T(".",{size:22,color:INK})]));
  }
  // 11, Miscellaneous terms (approved, verbatim)
  c.push(h1("11. Miscellaneous terms"));
  AC.MISC_TERMS.forEach(mt=>c.push(P([T(mt.title+" ",{size:22,bold:true,color:NAVY2}),T(mt.body,{size:22,color:INK})])));
  // signatures
  c.push(h1("Acceptance and signatures"));
  c.push(clzP(AC.SIGNATURE_PREAMBLE,{DATE:reason(ctx.returnBy,"Signature","return-by date","offer-expiry date for signature","not in quote")},{keepNext:true}));
  c.push(P([T(AC.AUTHORITY_BIND,{size:22,bold:true,color:INK})],{keepNext:true}));
  c.push(table([4680,4680],[[hd(provider.legalName),hd("Client")],
    [[T("Signature:",{size:20,color:INK}),new TextRun({break:2}),T("Name:",{size:20,color:INK}),new TextRun({break:1}),T("Title:",{size:20,color:INK}),new TextRun({break:1}),T("Date:",{size:20,color:INK})],
     [T("Signature:",{size:20,color:INK}),new TextRun({break:2}),T("Name:",{size:20,color:INK}),new TextRun({break:1}),T("Title:",{size:20,color:INK}),new TextRun({break:1}),T("Date:",{size:20,color:INK})]]]));
  // Exhibit A, build variants only; assessments fix scope by the Section 4 deliverable list
  if(!isAssess){
  c.push(new Paragraph({children:[new PageBreak()]}));
  c.push(h1("Exhibit A. Basis of estimate"));
  if(Array.isArray(m.basisOfEstimate)&&m.basisOfEstimate.length){
    // Curated basis-of-estimate (preferred): Dimension / Assumed footprint, plus an optional lines-of-code basis note.
    c.push(P([T("This Basis of Estimate records the current-state footprint Service Provider priced against, incorporated into the Statement of Work by reference. The figures describe the basis of the estimate, not a fixed quantity of work or a guarantee of the Client's current state.",{size:22,color:INK})]));
    c.push(P([T("Estimation assumptions",{size:22,bold:true,color:NAVY2})]));
    c.push(table([4680,4680],[[hd("Dimension"),hd("Assumed footprint")],
      ...m.basisOfEstimate.map(e=>[[T(e.dimension,{size:20,color:INK})],[T(String(e.footprint),{size:20,color:INK})]])]));
    if(m.locBasisNote)c.push(P([T(m.locBasisNote,{size:20,color:INK})]));
    log.push(["Exhibit A","basis of estimate",m.basisOfEstimate.length+" curated dimensions","model.basisOfEstimate",false]);
  } else {
    c.push(P([T("This estimate assumes the volumetric footprint below, mined from the scope assumptions. Values are confirmed during the Analyze phase. Additions beyond these volumes are Change Orders.",{size:22,color:INK})]));
    const exhibitRows=(Array.isArray(m.exhibitA)&&m.exhibitA.length)?m.exhibitA:exhibitA;
    c.push(table([5760,3600],[[hd("Volumetric assumption"),hd("Scope item")],
      ...(exhibitRows.length?exhibitRows.map(e=>[[T(e.text,{size:20,color:INK})],[T(e.item,{size:18,color:STEEL})]]):[[[flag("no volumetrics found in assumptions, review")],""]])]));
    log.push(["Exhibit A","volumetric assumptions",(m.exhibitA?m.exhibitA.length+" model-supplied":exhibitA.length+" mined from assumptions"),m.exhibitA?"model.exhibitA":"scope item assumptions",exhibitRows.length===0]);
  }
  }
  // Appendix A (assess only): instruments and methods, sourced from canonical/instruments/. This is the
  // assessment equivalent of Exhibit A, a methodological basis rather than a volumetric one.
  if(isAssess&&Array.isArray(m.instruments)&&m.instruments.length){
    c.push(new Paragraph({children:[new PageBreak()]}));
    c.push(h1("Appendix A. Assessment instruments and methods"));
    c.push(P([T("This assessment is conducted with the instruments below, Service Provider's standard methods for this engagement type. They are named so the findings can be read against a stated basis and a cited source.",{size:22,color:INK})]));
    const irow=(k,v)=>[[T(k,{size:20,bold:true,color:INK})],[T(v||"",{size:20,color:INK})]];
    m.instruments.forEach(ins=>{c.push(h3(ins.name));
      c.push(table([2600,6760],[irow("What it measures",ins.measures),irow("Scale",ins.scale),irow("Grounded in",ins.grounding),irow("Output",ins.output)]));
      log.push(["Appendix A","instrument: "+ins.name,ins.source?("rendered from "+ins.source):"rendered","model.instruments",false]);});
  }
  return c;}

// Letter of Engagement (variant "loe"): a short engagement letter under the PSA for lightweight motions
// (e.g. the fd-dd rapid screen) that a 27-clause SOW over-serves. Reuses the SOW styling and approved
// clauses (PSA incorporation, fixed fee, invoices, expenses, order-of-precedence, signature).
function buildLetter(){const c=[];delivCount=items.length;
  if(input.contract.status==="example")c.push(P([T("Synthetic example for skill testing",{bold:true})]));
  if(input.args["--draft"])c.push(P([T("Working draft with unresolved inputs",{bold:true})]));const clientName=ctx.accountName||null;
  if(LOGO)c.push(new Paragraph({spacing:{after:200},children:[new ImageRun({type:logoType,data:fs.readFileSync(LOGO),transformation:logoSize,altText:{title:provider.legalName,description:"logo",name:"logo"}})]}));
  c.push(new Paragraph({style:"Title",spacing:{before:120,after:60},children:[T("Letter of Engagement")]}));
  c.push(new Paragraph({spacing:{after:40},children:[T(ctx.opportunityName||"Advisory engagement",{size:24,color:TEAL})]}));
  c.push(P([T("Prepared for  ",{size:22,color:STEEL}),eng(ctx.accountName,"LOE","accountName","projectContext.accountName"),T("   •   Prepared by  ",{size:22,color:STEEL}),T(provider.legalName,{size:22,color:INK})]));
  c.push(table([4680,4680],[[hd("Investment"),hd("Timing")],
    [[eng(money(sum.totalValue),"LOE","fee","projectSummary.totalValue"),T("  (fixed fee)",{size:20,color:STEEL})],[T(m.durationLabel||(sum.durationWeeks+" week(s)"),{size:22,color:INK})]]]));
  c.push(clzP(AC.PREAMBLE,{CLIENT:clientName||"[CLIENT LEGAL NAME — confirm]"}));
  c.push(P([T("Professional Services Agreement Effective Date:  ",{size:22,bold:true,color:INK}),reason(ctx.psaEffectiveDate,"LOE","PSA effective date","blank if first SOW; else original PSA date","not in quote")]));
  c.push(h2("Purpose"));
  const purpose=ctx.businessNeed||m.purposeNarrative||((ctx.accountName||"The Client")+" has engaged Service Provider for "+(ctx.opportunityName||"a rapid advisory screen")+". This letter sets out the scope, fee, and terms of that engagement under the Professional Services Agreement.");
  c.push(P([T(String(purpose),{size:22,color:INK})]));
  if(!ctx.businessNeed&&!m.purposeNarrative)log.push(["LOE","purpose","INFERRED from quote signals — confirm","reasoned",true]);
  c.push(h2("What we will do"));
  items.forEach(si=>{const d=si.description?stripHtml(si.description):null;c.push(bull([T(si.name+(d?": ":""),{size:22,bold:true,color:INK}),d?T(d,{size:22,color:INK}):flag(si.name+" description missing")]));});
  c.push(h2("Fee"));
  c.push(clzP(AC.LOE_FIXED_CLOSE,{TOTAL:money(sum.totalValue)}));
  c.push(P([T("Estimated at ",{size:22,color:INK}),eng(sum.totalHours,"LOE","totalHours","projectSummary.totalHours"),T(" hours. The fee is fixed regardless of actual hours.",{size:22,color:INK})]));
  c.push(clzP(AC.FIXED_INVOICES));
  c.push(clzP(AC.EXPENSES_CARVEOUT));
  c.push(h2("Timing"));
  c.push(clzP(AC.COMMENCEMENT_STAFFING_ASSESS));
  c.push(P([T("The engagement window is "+band.startDate+" to "+band.endDate+".",{size:22,color:INK})]));
  c.push(h2("Assumptions and limits"));
  items.forEach(si=>{if(!si.assumptions)return;const a=stripHtml(si.assumptions);const cond=sentences(a).filter(s=>!CO.test(s)).join(". ");c.push(bull([T(si.name+": ",{size:22,bold:true,color:INK}),T((cond?cond+".":a),{size:22,color:INK})]));});
  c.push(P([reason(m.engagementBoundary,"LOE","engagement boundary","state the limits of the engagement","model.engagementBoundary")]));
  c.push(h2("Terms"));
  AC.MISC_TERMS.filter(mt=>/Order of Precedence|Limited Modification/.test(mt.title)).forEach(mt=>c.push(P([T(mt.title+" ",{size:22,bold:true,color:NAVY2}),T(mt.body,{size:22,color:INK})])));
  c.push(clzP(AC.LOE_ACCEPTANCE));
  c.push(clzP(AC.SIGNATURE_PREAMBLE,{DATE:reason(ctx.returnBy,"LOE","return-by date","offer-expiry date","not in quote")},{keepNext:true}));
  c.push(P([T(AC.AUTHORITY_BIND,{size:22,bold:true,color:INK})],{keepNext:true}));
  c.push(table([4680,4680],[[hd(provider.legalName),hd("Client")],
    [[T("Signature:",{size:20,color:INK}),new TextRun({break:2}),T("Name:",{size:20,color:INK}),new TextRun({break:1}),T("Title:",{size:20,color:INK}),new TextRun({break:1}),T("Date:",{size:20,color:INK})],
     [T("Signature:",{size:20,color:INK}),new TextRun({break:2}),T("Name:",{size:20,color:INK}),new TextRun({break:1}),T("Title:",{size:20,color:INK}),new TextRun({break:1}),T("Date:",{size:20,color:INK})]]]));
  return c;}

const outstanding=[...draftIssues,...flags.map(f=>f.join(": ")),...log.filter(r=>r[4]).map(r=>r[0]+": "+r[1])];
if(outstanding.length&&!input.args["--draft"]) {
  fs.mkdirSync(path.dirname(input.output),{recursive:true});
  fs.writeFileSync(input.output+".build.json",JSON.stringify({state:"not-built",errors:outstanding,...input.sources},null,2));
  console.error("Unresolved inputs. Supply them, or use --draft for a marked working copy:\n"+outstanding.join("\n"));process.exit(2);
}
Packer.toBuffer(doc).then(b=>{
  const path=require("path");
  const variantName=isLoe?"LOE":isAssess?"Assess":isAgile?"Agile":"Waterfall";
  // STRUCTURE.md approach B: "<10> <Short Name> - <Artifact>[ - <Band>].docx", filed under {Shape}/{Full Playbook Name}/.
  // Identity comes from the model (shape/playbookName/shortName, sourced from catalog.json); the code never appears in the name.
  const shortName=m.shortName||ctx.playbookName||ctx.quoteName;
  const fullName=m.playbookName||shortName;
  const shape=m.shape||(isLoe?"Front Door":isAssess?"Assess":"Implement");
  const artifactLabel=isLoe?"Letter of Engagement":"SOW";
  const bandName=(isAssess||isLoe)?null:(m.bandName||(band&&band.name)||null);  // assess prices additively, no band
  const fileBase=`10 ${shortName} - ${artifactLabel}${bandName?(" - "+bandName):""}`;
  const out=input.output,dir=path.dirname(out);fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(out,b);
  console.log("\n=== RECONCILIATION ===");rec.lines.forEach(l=>console.log(l));
  let md=`# Resolution Log, ${ctx.quoteName} (${variant})\n\nGenerated ${new Date().toISOString().slice(0,10)} by sow.\n\n`;
  md+=`## Reconciliation (three-way tie)\n\n\`\`\`\n${rec.lines.join("\n")}\n\`\`\`\n\n`;
  md+=`## Derived sections (mined from scope assumptions)\n\n- Consolidated assumptions (Section 7.2): ${items.filter(i=>i.assumptions).length}\n- Change-Order triggers (Section 8.1): ${coTriggers.length}\n${isAssess?"- Exhibit A: not applicable (assess fixes scope by the Section 4 deliverable list)":"- Exhibit A volumetrics: "+exhibitA.length}\n- Deliverables (Section 4): ${delivCount}\n\n`;
  md+=`## Placeholder resolution\n\n| Section | Placeholder | Value | Source | Flagged |\n|---|---|---|---|---|\n`;
  log.forEach(r=>md+=`| ${r[0]} | ${r[1]} | ${String(r[2]).replace(/\|/g,"/")} | ${r[3]} | ${r[4]?"YES":""} |\n`);
  md+=`\n## Scope & assumptions flag pass\n\n`;
  if(!flags.length)md+="No issues, every scope item has a description and assumptions.\n";
  else{md+=`| Scope item | Issue | Action |\n|---|---|---|\n`;flags.forEach(f=>md+=`| ${f[0]} | ${f[1]} | ${f[2]} |\n`);}
  const nF=log.filter(r=>r[4]).length;
  md+=`\n## Summary\n\n- Placeholders/derivations logged: ${log.length}\n- Flagged (missing source — NOT fabricated): ${nF}\n- Scope/assumption issues: ${flags.length}\n- Three-way tie: ${rec.tie?"PASS":"FAIL"}\n`;
  // Resolution log is a build input, not a numbered deliverable, so it lives in the folder's _source/.
  const srcDir=path.join(dir,"_source");fs.mkdirSync(srcDir,{recursive:true});
  const logOut=path.join(srcDir,path.basename(out,".docx")+" - Resolution Log.md");fs.writeFileSync(logOut,md);
  fs.writeFileSync(out+".build.json",JSON.stringify({state:"built",artifact:out,variant,
    synthetic:input.contract.status==="example",unresolved:outstanding,reconciliation:rec,
    artifactSha256:require("crypto").createHash("sha256").update(b).digest("hex"),
    brandProfile:brand.tokensPath,brandSha256:brand.provenance.sourceSha256,...input.sources},null,2));
  console.log(`\nWROTE ${out}`);console.log(`     log ${logOut}`);console.log(`Flagged: ${nF}/${log.length} | scope issues: ${flags.length} | CO triggers: ${coTriggers.length} | Exhibit A: ${exhibitA.length} | assumptions: ${items.filter(i=>i.assumptions).length}`);
}).catch(error=>{console.error(error.stack||error.message);process.exitCode=2;});
