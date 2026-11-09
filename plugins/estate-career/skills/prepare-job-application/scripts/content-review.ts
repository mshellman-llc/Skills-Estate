import { createHash } from 'node:crypto';
export const digest = (s: string) => createHash('sha256').update(s).digest('hex');
export type Brief = { audience: 'internal'|'hiring'|'public'|'client'|'personal'; purpose: string; readerAction: string; voice: string; risk: 'routine'|'consequential' };
export type Review = { brief: Brief; bodyHash: string; depth: 'light'|'standard'|'deep'; reviewer: string; sources: {id:string;revision:number;hash:string}[]; coverage: {dimension:string;action:'covered'|'omitted';quote:string;reason:string}[]; checks: Record<'accuracy'|'representation'|'writing'|'layout',{result:'pass'|'fail'|'not-applicable';notes:string}> };
const nonempty = (v: unknown): v is string => typeof v==='string' && v.trim().length>0;
export function plan(brief: Brief) {
 if (!brief || !['internal','hiring','public','client','personal'].includes(brief.audience) || !nonempty(brief.purpose) || brief.purpose.length>80 || !nonempty(brief.readerAction) || !nonempty(brief.voice) || !['routine','consequential'].includes(brief.risk)) throw new Error('Declare audience, purpose, reader action, voice, and risk.');
 if (brief.purpose==='resume' && brief.audience!=='hiring') throw new Error('A resume requires a hiring audience. Use a different purpose for a handout.');
 const depth = brief.risk==='consequential'||['resume','proposal','portfolio'].includes(brief.purpose)||['hiring','client','public'].includes(brief.audience)?'deep':brief.purpose==='update'?'light':'standard';
 const dimensions = brief.purpose==='resume'?['career-progression','leadership-scope','client-decision','commercial-ownership','major-results']:brief.purpose==='portfolio'?['problem','ownership','mechanism','result']:brief.purpose==='proposal'?['problem','scope','commercial-terms','dependencies']:['update','working-notes'].includes(brief.purpose)?['reader-need','next-action']:['reader-need','essential-content'];
 return {depth,dimensions,style:'Audience and intended reader action govern register, detail, structure, and vocabulary. Preserve the author voice within that task. Do not apply a word blacklist, invent facts, or claim an AI-detector score.',review: depth==='light'?'Check clarity, facts, privacy, and action; preserve concise fragments and genuine lists.':'Read the complete draft for factual meaning, ownership, omitted scope, reader comprehension, and formulaic or generic prose. Layout checks are separate from writing checks.',limits:'This gate verifies review structure and exact source/content bindings. Semantic accuracy, relevance, and voice require substantive review; declarations are not independent proof.'};
}
export function validateReview(body: string, brief: Brief, r: Review, source: (id:string)=>{revision:number;hash:string;body?:string}) {
 const p=plan(brief);
 if (!r || !r.brief || (['audience','purpose','readerAction','voice','risk'] as const).some(k=>r.brief[k]!==brief[k]) || r.bodyHash!==digest(body)) throw new Error('Content review is missing or does not match the current body and brief.');
 if (r.depth!==p.depth || !nonempty(r.reviewer)) throw new Error('Review depth must follow audience/purpose/risk and identify its reviewer.');
 if (!Array.isArray(r.sources) || !r.sources.length) throw new Error('A content review requires the source foundation.');
 const ids=new Set<string>();
 for(const s of r.sources){if(ids.has(s.id))throw new Error('Duplicate review source.');ids.add(s.id);const current=source(s.id);if(s.revision!==current.revision||s.hash!==current.hash)throw new Error('Review source changed; reread and review the new revision.');}
 if (!Array.isArray(r.coverage)) throw new Error('Representation coverage is required.');
 for(const dim of p.dimensions){const rows=r.coverage.filter(c=>c.dimension===dim);if(rows.length!==1)throw new Error('Coverage must address '+dim+' exactly once.');const c=rows[0];if(!nonempty(c.reason))throw new Error('Coverage needs audience-specific reasoning.');if(c.action==='covered'){if(!nonempty(c.quote)||!body.includes(c.quote))throw new Error('Coverage excerpt missing from draft: '+dim);}else if(c.action!=='omitted'||(brief.purpose==='resume'&&['career-progression','leadership-scope'].includes(dim)))throw new Error('Required representation cannot be omitted: '+dim);}
 for(const k of ['accuracy','representation','writing','layout'] as const){const c=r.checks?.[k];if(!c||!nonempty(c.notes)||!(c.result==='pass'||(k==='layout'&&c.result==='not-applicable')))throw new Error('Separate '+k+' review must pass with concrete notes.');}
 return p;
}
