import fs from 'node:fs';
import {validateReview} from './content-review.ts';
try { const x=JSON.parse(fs.readFileSync(0,'utf8')); const result=validateReview(x.body,x.brief,x.review,(id:string)=>{const s=x.sources[id];if(!s)throw new Error('Missing source '+id);return s;});console.log(JSON.stringify({ok:true,plan:result})); } catch(e) {console.error(e instanceof Error?e.message:String(e));process.exitCode=1;}
