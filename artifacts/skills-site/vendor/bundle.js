/* @ds-bundle: {"format":4,"namespace":"LLC","components":[{"name":"Wordmark"},{"name":"SpecPlaque"},{"name":"PersonalPlaque"},{"name":"DiffPatch"},{"name":"DiffPill"},{"name":"Icon"},{"name":"Logo"},{"name":"Button"},{"name":"IconButton"},{"name":"Tag"},{"name":"StateText"},{"name":"Avatar"},{"name":"Field"},{"name":"Search"},{"name":"Checkbox"},{"name":"Toggle"},{"name":"Tabs"},{"name":"Segmented"},{"name":"Breadcrumb"},{"name":"Pagination"},{"name":"FactBand"},{"name":"DetailPanel"},{"name":"DecisionList"},{"name":"WeekStrip"},{"name":"DealBoard"},{"name":"StageSpine"},{"name":"ColumnChart"},{"name":"EmptyState"},{"name":"Sidebar"},{"name":"TopBar"},{"name":"Conversation"},{"name":"Dialog"},{"name":"Toast"},{"name":"Tooltip"},{"name":"Menu"},{"name":"FilterBar"},{"name":"Skeleton"},{"name":"Progress"},{"name":"Callout"},{"name":"ProposedChange"},{"name":"Grounds"},{"name":"Quote"},{"name":"AgentActivity"},{"name":"SectionChanges"},{"name":"StatusBadge"},{"name":"PhaseTimeline"},{"name":"CellReveal"},{"name":"Divider"},{"name":"TierPicker"},{"name":"AvatarStack"}]} */
/* LiveLaughCode marks: Wordmark, SpecPlaque, PersonalPlaque, DiffPatch, DiffPill. Only the Code_ pill carries the brand gradient. */
;(function () {
  var React = window.React, h = React.createElement;
  function cx() { return Array.prototype.filter.call(arguments, Boolean).join(' '); }
  function Prompt(p) {
    return h('svg', { className: 'llc-cue', width: p && p.w || 18, height: p && p.h || 12, viewBox: '0 0 20 14', fill: 'none', 'aria-hidden': 'true' },
      h('path', { d: 'M 2 2.5 L 8.5 7 L 2 11.5', stroke: 'currentColor', strokeWidth: 2.5, strokeLinecap: 'round', strokeLinejoin: 'round' }),
      h('rect', { x: 11, y: 9.5, width: 7.5, height: 2.5, rx: 1.25, fill: 'currentColor' }));
  }
  function Code(cls) { return h('span', { className: cls }, 'Code', h('span', { className: 'llc-cursor' }, '_')); }
  function Meta(p) {
    var m = p.meta || [];
    return h('div', { className: cx('llc-meta', p.top && 'llc-meta-top', p.className) }, h('span', null, m[0]), h('span', null, m[1]));
  }
  function Wordmark(p) {
    p = p || {};
    var size = p.size || 'lg', attribution = p.attribution || 'none';
    var mark = h('span', { className: cx('llc-wordmark', 'llc-wordmark-' + size), role: 'img', 'aria-label': 'Live, Laugh, Code' },
      h('span', { className: 'llc-serif llc-wordmark-live', 'aria-hidden': 'true' }, 'Live, Laugh,'),
      h('span', { className: 'llc-code-pill', 'aria-hidden': 'true' }, 'Code', h('span', { className: 'llc-cursor' }, '_')));
    if (attribution === 'inline') {
      return h('span', { className: cx('llc-sig-inline', p.className) }, mark, h('span', { className: 'llc-divider', 'aria-hidden': 'true' }), h('span', { className: 'llc-sig-name' }, p.name || 'Megan Shellman'));
    }
    if (attribution === 'stacked') {
      return h('span', { className: cx('llc-sig-stacked', p.className) }, mark, h('span', { className: 'llc-sig-sub' }, p.subline || 'By Megan Shellman · Cofounder - RevTech & Applied AI'));
    }
    return p.className ? h('span', { className: p.className }, mark) : mark;
  }
  function SpecPlaque(p) {
    p = p || {};
    return h('div', { className: cx('llc-plaque', p.className), role: 'group', 'aria-label': 'Live, Laugh, Code spec plaque' },
      h('div', { className: 'llc-row' }, h('span', { className: 'llc-index' }, '01'), h('span', { className: 'llc-serif llc-plaque-word' }, 'Live')),
      h('div', { className: 'llc-row' }, h('span', { className: 'llc-index' }, '02'), h('span', { className: 'llc-serif llc-plaque-word' }, 'Laugh')),
      h('div', { className: 'llc-row llc-row-active' }, h('span', { className: 'llc-index' }, '03'), Code('llc-plaque-code')),
      h(Meta, { meta: p.meta || ['LiveLaughCode LLC', 'Est. 2023'] }));
  }
  function PersonalPlaque(p) {
    p = p || {};
    return h('div', { className: cx('llc-plaque llc-plaque-personal', p.className) },
      h(Meta, { top: true, meta: p.topMeta || ['LiveLaughCode', 'M. Shellman'] }),
      h('div', { className: 'llc-row llc-row-name' },
        h('div', null, h('div', { className: 'llc-person' }, p.name || 'Megan Shellman'), h('div', { className: 'llc-serif llc-person-tag' }, p.tagline || 'RevTech & Applied AI')),
        h('span', { className: 'llc-chip', 'aria-label': (p.initial || 'M') + ' prompt' }, h('span', null, p.initial || 'M'), h('span', { className: 'llc-accent' }, h(Prompt, { w: 11, h: 9 })))),
      h(Meta, { meta: p.meta || ['Cofounder', 'Marietta, GA'] }));
  }
  function DiffPatch(p) {
    p = p || {};
    return h('div', { className: cx('llc-patch', p.className) },
      h('div', { className: 'llc-patch-head' }, h('span', null, 'Patch · ' + (p.version || 'v2.0')), h('span', null, 'LiveLaughCode')),
      h('div', { className: 'llc-patch-body' },
        h('div', { className: 'llc-serif llc-patch-live' }, 'Live, Laugh,'),
        h('del', { className: 'llc-diff llc-diff-del' }, h('span', { className: 'llc-diff-sign' }, '−'), h('span', { className: 'llc-serif llc-strike llc-diff-love' }, 'Love')),
        h('ins', { className: 'llc-diff llc-diff-add' }, h('span', { className: 'llc-diff-sign llc-accent' }, '+'), Code('llc-diff-code'), h('span', { className: 'llc-diff-note' }, p.note || 'shipped'))),
      h(Meta, { meta: p.meta || ['RevTech & Applied AI', 'Megan Shellman'] }));
  }
  function DiffPill(p) {
    p = p || {};
    return h('span', { className: cx('llc-diff-pill', p.className), role: 'img', 'aria-label': 'Live, Laugh, Love replaced by Code' },
      h('span', { className: 'llc-serif llc-pill-live', 'aria-hidden': 'true' }, 'Live, Laugh,'),
      h('span', { className: 'llc-serif llc-strike llc-pill-love', 'aria-hidden': 'true' }, 'Love'),
      h('span', { className: 'llc-pill-rule', 'aria-hidden': 'true' }),
      h('span', { className: 'llc-pill-code', 'aria-hidden': 'true' }, 'Code', h('span', { className: 'llc-cursor' }, '_')));
  }
  window.LLCMarks = { Wordmark: Wordmark, SpecPlaque: SpecPlaque, PersonalPlaque: PersonalPlaque, DiffPatch: DiffPatch, DiffPill: DiffPill };
})();
/* Interaction patterns: behavior for the interaction components. Runs once when the page is ready and does not need React. After adding markup later, call window.LLCInteractions.init(root). */
;(function(){
function fresh(root,sel,key){return [].slice.call(root.querySelectorAll(sel)).filter(function(el){var m=el.__ixInit||(el.__ixInit={});if(m[key])return false;m[key]=1;return true})}
var RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function ixCount(el,to,ms){if(RM){el.textContent=to;return}var from=+el.textContent||0,t0=performance.now();function st(t){var k=Math.min(1,(t-t0)/ms),e=1-Math.pow(1-k,3);el.textContent=Math.round(from+(to-from)*e);if(k<1)requestAnimationFrame(st)}requestAnimationFrame(st)}
function ixView(el,fn){if(RM||!('IntersectionObserver' in window)){fn();return}var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){fn();io.disconnect()}},{threshold:.4});io.observe(el)}
var IXX='<svg class="ixi" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
var inits=[
  /* DifferenceToggle */ function(Q){Q('.ix-dt').forEach(function(r){var s=r.querySelector('.ix-sw'),d=r.querySelector('.ix-diff');s.addEventListener('click',function(){var on=s.getAttribute('aria-pressed')!=='true';s.setAttribute('aria-pressed',on);d.classList.toggle('is-only',on)})});},
  /* HotspotPins */ function(Q){Q('.ix-hs').forEach(function(r){var ps=[].slice.call(r.querySelectorAll('.ix-nm')),n=r.querySelector('.ix-hs-n');ps.forEach(function(p){p.addEventListener('click',function(){var o=p.getAttribute('aria-expanded')==='true';ps.forEach(function(q){q.setAttribute('aria-expanded','false')});if(o){n.classList.remove('is-on')}else{p.setAttribute('aria-expanded','true');n.querySelector('small').textContent=p.textContent+' of '+ps.length;n.querySelector('span').textContent=p.getAttribute('data-t');n.classList.add('is-on')}})})});},
  /* MilestoneScrubber */ function(Q){Q('.ix-msr').forEach(function(r){var t=r.querySelector('.ix-trk'),i=t.querySelector('input'),ph=r.querySelectorAll('.ix-ms div'),d=r.querySelector('.ix-ms-d');
function set(){var v=+i.value,k=Math.min(ph.length-1,Math.floor(v/(100/ph.length)));t.style.setProperty('--p',v+'%');ph.forEach(function(p,j){p.classList.toggle('is-on',j===k);p.classList.toggle('is-done',j<k)});d.textContent='Phase '+(k+1)+' of '+ph.length+'. What happens in this phase goes here.'}
i.addEventListener('input',set);set()});},
  /* StepSequence */ function(Q){Q('.ix-stp').forEach(function(r){var k=0,bs=r.querySelectorAll('.ix-st .ix-nm'),us=r.querySelectorAll('.ix-st u'),ss=r.querySelectorAll('.ix-st-v > div'),b=r.querySelector('[data-d="-1"]'),f=r.querySelector('[data-d="1"]'),n=bs.length;
function set(){bs.forEach(function(x,j){x.classList.toggle('is-on',j<=k);if(j===k)x.setAttribute('aria-current','step');else x.removeAttribute('aria-current')});us.forEach(function(x,j){x.classList.toggle('is-done',j<k)});ss.forEach(function(x,j){x.classList.toggle('is-on',j===k)});b.disabled=k===0;f.textContent=k===n-1?'Start over':'Next'}
f.addEventListener('click',function(){k=k===n-1?0:k+1;set()});b.addEventListener('click',function(){k=Math.max(0,k-1);set()});set()});},
  /* ReadingProgress */ function(Q){Q('.ix-rp').forEach(function(r){var s=r.querySelector('.ix-rp-s'),ch=s.querySelectorAll('section'),ds=r.querySelectorAll('.ix-rp-d .ix-nm');
function set(){var m=(s.scrollHeight-s.clientHeight)||1,p=s.scrollTop/m,k=0;r.style.setProperty('--p',(p*100)+'%');ch.forEach(function(c,j){if(c.offsetTop-s.offsetTop<=s.scrollTop+40)k=j});if(p>.98)k=ch.length-1;ds.forEach(function(d,j){d.classList.toggle('is-on',j<=k)})}
s.addEventListener('scroll',set);set()});},
  /* ScrollTextHighlight */ function(Q){Q('.ix-th').forEach(function(t){var p=t.querySelector('p');p.innerHTML=p.textContent.split(' ').map(function(x){return '<span>'+x+'</span>'}).join(' ');var sp=p.querySelectorAll('span');
function set(){var m=(t.scrollHeight-t.clientHeight)||1,k=Math.round((t.scrollTop/m)*sp.length*1.05)+3;sp.forEach(function(s,j){s.classList.toggle('is-on',j<k)})}
t.addEventListener('scroll',set);set()});},
  /* ChartPointSnap: labels and the point are HTML over the chart, so they keep their shape at any width */ function(Q){Q('.ix-chr').forEach(function(r){var w=r.querySelector('.ix-ch'),svg=w.querySelector('svg'),d=w.querySelector('.ix-ch-d'),g=svg.querySelector('line'),tip=w.querySelector('.ix-ch-t'),rp=r.querySelector('[data-replay]'),pts=[[10,130],[60,110],[110,96],[160,70],[210,52],[260,28]];
if(!w.classList.contains('is-static')){if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){w.classList.add('is-drawn');io.disconnect()}},{threshold:.4});io.observe(w)}else w.classList.add('is-drawn');
if(rp)rp.addEventListener('click',function(){w.classList.add('is-reset');w.classList.remove('is-drawn');void w.offsetWidth;w.classList.remove('is-reset');requestAnimationFrame(function(){requestAnimationFrame(function(){w.classList.add('is-drawn')})})})}
function mv(e){var b=svg.getBoundingClientRect(),x=((e.touches?e.touches[0].clientX:e.clientX)-b.left)/b.width*320,n=pts[0];pts.forEach(function(p){if(Math.abs(p[0]-x)<Math.abs(n[0]-x))n=p});if(d){d.style.left=(14+n[0]/320*b.width)+'px';d.style.top=(14+n[1]/170*b.height)+'px';d.style.opacity=1}g.setAttribute('x1',n[0]);g.setAttribute('x2',n[0]);g.style.opacity=.4;tip.style.left=(14+n[0]/320*b.width)+'px';tip.textContent='Point '+(pts.indexOf(n)+1)+' of '+pts.length;tip.style.opacity=1}
function out(){if(d)d.style.opacity=0;g.style.opacity=0;tip.style.opacity=0}
svg.addEventListener('mousemove',mv);svg.addEventListener('touchstart',mv,{passive:true});svg.addEventListener('touchmove',mv,{passive:true});svg.addEventListener('mouseleave',out)});},
  /* ColumnHighlight */ function(Q){Q('.br-coltable').forEach(function(t){function set(i){t.querySelectorAll('.is-col').forEach(function(c){c.classList.remove('is-col')});if(i<1)return;t.querySelectorAll('tr').forEach(function(r){var c=r.children[i];if(c)c.classList.add('is-col')})}
function on(e){var c=e.target.closest('td,th');if(c)set(c.cellIndex)}
t.addEventListener('mouseover',on);t.addEventListener('focusin',on);t.addEventListener('mouseleave',function(){set(-1)});t.addEventListener('focusout',function(){set(-1)});});},
  /* GuidedWalkthrough */ function(Q){Q('.br-tour').forEach(function(root){var scr=root.querySelector('.br-tour-screen'),ts=[].slice.call(root.querySelectorAll('[data-step]')),card=root.querySelector('.br-tour-card'),i=-1;
function q(s){return card.querySelector(s)}
function go(n){i=n;ts.forEach(function(t,k){t.classList.toggle('is-focus',k===n)});if(n<0){scr.style.transform='';root.classList.remove('is-on');return}
var t=ts[n],z=Math.max(1,Math.min(1.5,root.clientWidth*.5/t.offsetWidth,root.clientHeight*.7/t.offsetHeight)),cx=t.offsetLeft+t.offsetWidth/2,cy=t.offsetTop+t.offsetHeight/2;
scr.style.transform='translate('+(root.clientWidth*.32-cx*z)+'px,'+(root.clientHeight*.5-cy*z)+'px) scale('+z+')';root.classList.add('is-on');
q('[data-count]').textContent=(n+1)+' of '+ts.length;q('[data-title]').textContent=t.getAttribute('data-title');q('[data-text]').textContent=t.getAttribute('data-text');
q('[data-back]').disabled=n===0;q('[data-next]').textContent=n===ts.length-1?'Done':'Next'}
root.querySelector('[data-start]').addEventListener('click',function(){go(0)});
q('[data-back]').addEventListener('click',function(){go(i-1)});
q('[data-next]').addEventListener('click',function(){go(i===ts.length-1?-1:i+1)});
q('[data-close]').addEventListener('click',function(){go(-1)});
ts.forEach(function(t,k){t.querySelector('button').addEventListener('click',function(){go(k)})});});},
  /* TiltStack */ function(Q){Q('.br-tilt').forEach(function(box){var cs=[].slice.call(box.querySelectorAll('.br-tilt-card')),n=cs.length,rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function upd(){var p=box.scrollTop/((box.scrollHeight-box.clientHeight)||1)*(n-1);cs.forEach(function(c,j){var t=Math.max(0,Math.min(1,p-j)),wait=Math.max(0,j-p);c.style.zIndex=n-j;if(rm){c.style.visibility=j<Math.round(p)?'hidden':'visible';return}
if(j===n-1)t=0;c.style.transform='translateY('+(-t*340+wait*10)+'px) rotateX('+(t*58)+'deg) scale('+(1-wait*0.05)+')';c.style.opacity=t>.98?0:1})}
box.addEventListener('scroll',upd);upd()});},
  /* LoadStagger */ function(Q){Q('.br-stagger').forEach(function(g){[].slice.call(g.children).forEach(function(c,i){c.style.setProperty('--i',i)});function play(){g.classList.remove('is-in');void g.offsetWidth;requestAnimationFrame(function(){g.classList.add('is-in')})}play();var b=g.parentNode&&g.parentNode.querySelector('[data-replay-stagger]');if(b)b.addEventListener('click',play)});},
  /* CountUp */ function(Q){Q('.br-count').forEach(function(el){var to=parseFloat(el.getAttribute('data-to')),dec=+(el.getAttribute('data-decimals')||0),pre=el.getAttribute('data-prefix')||'',suf=el.getAttribute('data-suffix')||'',ms=+(el.getAttribute('data-ms')||1200),rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function fmt(v){return pre+v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suf}
function run(){if(rm){el.textContent=fmt(to);return}var t0=null;function f(t){if(!t0)t0=t;var k=Math.min(1,(t-t0)/ms),e=1-Math.pow(1-k,3);el.textContent=fmt(to*e);if(k<1)requestAnimationFrame(f)}requestAnimationFrame(f)}
el.textContent=fmt(rm?to:0);if('IntersectionObserver' in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){run();io.disconnect()}},{threshold:.5});io.observe(el)}else run();
var b=el.closest('[data-count-wrap]');b=b&&b.querySelector('[data-replay-count]');if(b&&!b.__bound){b.__bound=1;b.addEventListener('click',function(){b.closest('[data-count-wrap]').querySelectorAll('.br-count').forEach(function(x){x.__rerun&&x.__rerun()})})}el.__rerun=run});},
  /* LogoStrip */ function(Q){Q('.br-logos').forEach(function(s){var r=s.querySelector('.br-logos-row');if(r&&!r.__dup){r.__dup=1;[].slice.call(r.children).forEach(function(c){var d=c.cloneNode(true);d.setAttribute('aria-hidden','true');r.appendChild(d)})}});},
  /* PhaseTimeline: a row with aria-controls opens its panel; one open at a time; selecting the open row again closes it */ function(Q){Q('.br-tl[data-expand]').forEach(function(tl){var rows=[].slice.call(tl.querySelectorAll('.br-tl-row[aria-controls]'));
function set(r){var shut=r.getAttribute('aria-current')==='true'&&r.getAttribute('aria-expanded')==='true';rows.forEach(function(x){var on=x===r,open=on&&!shut,p=document.getElementById(x.getAttribute('aria-controls'));x.setAttribute('aria-current',on?'true':'false');x.setAttribute('aria-expanded',open?'true':'false');if(p)p.classList.toggle('is-open',open)})}
rows.forEach(function(r){r.tabIndex=0;r.setAttribute('role','button');r.addEventListener('click',function(){set(r)});r.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();set(r)}})})});},
  /* PinnedSequence */ function(Q){Q('.br-pin').forEach(function(box){var rows=[].slice.call(box.querySelectorAll('.br-tl-row')),n=rows.length,cur=-1;
function show(k){if(k===cur)return;cur=k;rows.forEach(function(r,j){r.setAttribute('aria-current',j===k?'true':'false')});
box.querySelector('[data-title]').textContent=rows[k].getAttribute('data-title');box.querySelector('[data-cap]').textContent=rows[k].getAttribute('data-cap');box.querySelector('[data-count]').textContent=(k+1)+' of '+n}
function upd(){show(Math.round(box.scrollTop/((box.scrollHeight-box.clientHeight)||1)*(n-1)))}
box.addEventListener('scroll',upd);
rows.forEach(function(r,k){r.addEventListener('click',function(){box.scrollTop=k/(n-1)*(box.scrollHeight-box.clientHeight)})});upd();});},
  /* RangeWithValueBubble */ function(Q){Q('.ix-rg').forEach(function(r){var i=r.querySelector('input'),o=r.querySelector('output'),b=r.querySelector('.ix-rg-t b'),ks=r.querySelectorAll('.ix-rg-k i');
 function set(){var mn=+i.min,mx=+i.max,v=+i.value,f=(v-mn)/(mx-mn),w=i.clientWidth,x=12+f*Math.max(0,w-24);o.style.left=x+'px';b.style.width=x+'px';o.textContent=v+(v===1?' week':' weeks');ks.forEach(function(k,j){k.classList.toggle('is-on',j+mn<=v)})}
 i.addEventListener('input',set);i.addEventListener('pointerdown',function(){r.classList.add('is-drag')});['pointerup','pointercancel','blur','change'].forEach(function(ev){i.addEventListener(ev,function(){r.classList.remove('is-drag')})});
 window.addEventListener('resize',set);set()});},
  /* PriorityRanking */ function(Q){Q('.ix-rank').forEach(function(ol){var live=ol.parentNode.querySelector('.ix-live'),drag=null,sy=0;
 function items(){return [].slice.call(ol.children)}
 function num(){var its=items();its.forEach(function(li,j){li.querySelector('b').textContent=j+1;var bs=li.querySelectorAll('.ix-rank-m button');bs[0].disabled=j===0;bs[1].disabled=j===its.length-1})}
 function flip(fn){var its=items(),r0=its.map(function(x){return x.getBoundingClientRect().top});fn();num();if(RM)return;its.forEach(function(x,j){if(x===drag)return;var d=r0[j]-x.getBoundingClientRect().top;if(d){x.style.transition='none';x.style.transform='translateY('+d+'px)';requestAnimationFrame(function(){requestAnimationFrame(function(){x.style.transition='transform .25s ease';x.style.transform=''})})}})}
 function say(li){if(live)live.textContent=li.querySelector('span').textContent+', position '+(items().indexOf(li)+1)+' of '+items().length}
 ol.addEventListener('click',function(e){var b=e.target.closest('.ix-rank-m button');if(!b||b.disabled)return;var li=b.closest('li'),up=b.dataset.d==='-1';flip(function(){if(up)ol.insertBefore(li,li.previousElementSibling);else ol.insertBefore(li.nextElementSibling,li)});var bs=li.querySelectorAll('.ix-rank-m button');(bs[up?0:1].disabled?bs[up?1:0]:bs[up?0:1]).focus();say(li)});
 ol.addEventListener('pointerdown',function(e){var h=e.target.closest('.ix-rank-h');if(!h)return;e.preventDefault();drag=h.closest('li');sy=e.clientY;drag.classList.add('is-drag');drag.style.transition='none';try{h.setPointerCapture(e.pointerId)}catch(x){}});
 ol.addEventListener('pointermove',function(e){if(!drag)return;var dy=e.clientY-sy,n=drag.nextElementSibling,p=drag.previousElementSibling;
  if(n&&dy>n.offsetHeight/2+3){var hn=n.offsetHeight+6;flip(function(){ol.insertBefore(n,drag)});sy+=hn;dy=e.clientY-sy}
  else if(p&&dy<-(p.offsetHeight/2+3)){var hp=p.offsetHeight+6;flip(function(){ol.insertBefore(drag,p)});sy-=hp;dy=e.clientY-sy}
  drag.style.transform='translateY('+dy+'px)'});
 function end(){if(!drag)return;var d=drag;drag=null;d.style.transition='transform .2s ease';d.style.transform='';d.classList.remove('is-drag');say(d)}
 ol.addEventListener('pointerup',end);ol.addEventListener('pointercancel',end);
 ol.addEventListener('keydown',function(e){var h=e.target.closest('.ix-rank-h');if(!h)return;var li=h.closest('li');if(e.key==='ArrowUp'&&li.previousElementSibling){e.preventDefault();flip(function(){ol.insertBefore(li,li.previousElementSibling)});h.focus();say(li)}else if(e.key==='ArrowDown'&&li.nextElementSibling){e.preventDefault();flip(function(){ol.insertBefore(li.nextElementSibling,li)});h.focus();say(li)}});
 num()});},
  /* ConfidenceMeter */ function(Q){Q('.ix-mt').forEach(function(r){var wrap=r.querySelector('.ix-mt-b'),bs=[].slice.call(wrap.querySelectorAll('button')),l=r.querySelector('.ix-mt-l b'),c=r.querySelector('.ix-mt-l span'),names=['Low','Some','Moderate','High','Full'];
 function paint(n,cls){bs.forEach(function(b,j){b.classList.toggle(cls,j<=n)})}
 function set(n,f){paint(n,'is-on');bs.forEach(function(b,j){b.setAttribute('aria-checked',j===n);b.tabIndex=j===n?0:-1});l.textContent=names[n];c.textContent=(n+1)+' of 5';if(f)bs[n].focus()}
 bs.forEach(function(b,j){b.setAttribute('aria-label',names[j]);b.addEventListener('mouseenter',function(){wrap.classList.add('is-hover');paint(j,'is-pre')});b.addEventListener('click',function(){set(j)});b.addEventListener('keydown',function(e){var d=(e.key==='ArrowRight'||e.key==='ArrowUp')?1:(e.key==='ArrowLeft'||e.key==='ArrowDown')?-1:0;if(d){e.preventDefault();set(Math.max(0,Math.min(4,j+d)),1)}})});
 wrap.addEventListener('mouseleave',function(){wrap.classList.remove('is-hover');paint(-1,'is-pre')});set(2)});},
  /* CommandPalette */ function(Q){Q('.ix-cmd').forEach(function(r){var o=r.querySelector('.ix-cmd-open'),lay=r.querySelector('.ix-cmd-lay'),inp=lay.querySelector('input'),ul=r.querySelector('.ix-cmd-l'),lis=[].slice.call(ul.children),em=r.querySelector('.ix-cmd-e'),res=r.querySelector('.ix-cmd-res'),vis=lis.slice(),a=0;
 function act(n){a=n;lis.forEach(function(li){li.setAttribute('aria-selected','false')});var li=vis[n];if(!li){inp.removeAttribute('aria-activedescendant');return}li.setAttribute('aria-selected','true');inp.setAttribute('aria-activedescendant',li.id);if(li.offsetTop<ul.scrollTop)ul.scrollTop=li.offsetTop-6;else if(li.offsetTop+li.offsetHeight>ul.scrollTop+ul.clientHeight)ul.scrollTop=li.offsetTop+li.offsetHeight-ul.clientHeight+6}
 function filt(){var q=inp.value.trim().toLowerCase();vis=lis.filter(function(li){var on=li.textContent.toLowerCase().indexOf(q)>-1;li.hidden=!on;return on});em.hidden=vis.length>0;act(0)}
 function open(){r.classList.add('is-open');lay.setAttribute('aria-hidden','false');inp.setAttribute('aria-expanded','true');inp.value='';ul.scrollTop=0;filt();setTimeout(function(){inp.focus()},40)}
 function close(){if(!r.classList.contains('is-open'))return;r.classList.remove('is-open');lay.setAttribute('aria-hidden','true');inp.setAttribute('aria-expanded','false');o.focus()}
 function pick(li){res.innerHTML='Picked: <strong></strong>';res.querySelector('strong').textContent=li.querySelector('span').textContent;close()}
 o.addEventListener('click',open);
 r.addEventListener('keydown',function(e){if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();r.classList.contains('is-open')?close():open()}});
 inp.addEventListener('input',filt);
 inp.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){e.preventDefault();act(Math.min(vis.length-1,a+1))}else if(e.key==='ArrowUp'){e.preventDefault();act(Math.max(0,a-1))}else if(e.key==='Enter'){e.preventDefault();if(vis[a])pick(vis[a])}else if(e.key==='Escape'){e.preventDefault();close()}});
 lis.forEach(function(li){li.addEventListener('click',function(){pick(li)});li.addEventListener('mousemove',function(){var j=vis.indexOf(li);if(j!==a)act(j)})});
 lay.addEventListener('mousedown',function(e){if(e.target===lay)close()})});},
  /* SnapCarousel */ function(Q){Q('.ix-car').forEach(function(r){var s=r.querySelector('.ix-car-s'),sl=[].slice.call(s.children),ds=[].slice.call(r.querySelectorAll('.ix-car-d button')),pv=r.querySelector('[data-d="-1"]'),nx=r.querySelector('[data-d="1"]'),c=r.querySelector('.ix-car-c'),k=0,t;
 function cur(){var x=s.scrollLeft,best=0,bd=1e9;sl.forEach(function(e,j){var d=Math.abs(e.offsetLeft-2-x);if(d<bd){bd=d;best=j}});if(x>0&&x+s.clientWidth>=s.scrollWidth-4)best=sl.length-1;return best}
 function upd(){k=cur();ds.forEach(function(d,j){d.setAttribute('aria-current',j===k?'true':'false')});pv.disabled=k===0;nx.disabled=k===sl.length-1;c.textContent=(k+1)+' of '+sl.length}
 function go(j){s.scrollTo({left:sl[j].offsetLeft-2,behavior:RM?'auto':'smooth'})}
 s.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(upd,60)});
 pv.addEventListener('click',function(){go(Math.max(0,k-1))});nx.addEventListener('click',function(){go(Math.min(sl.length-1,k+1))});
 ds.forEach(function(d,j){d.addEventListener('click',function(){go(j)})});window.addEventListener('resize',upd);upd()});},
  /* UnderlineTabs */ function(Q){Q('.ix-ut').forEach(function(r){var bs=[].slice.call(r.querySelectorAll('[role="tab"]')),bar=r.querySelector('.ix-ut-l > i'),ps=[].slice.call(r.querySelectorAll('[role="tabpanel"]')),k=0;
 function set(j,f){k=j;bs.forEach(function(b,i){b.setAttribute('aria-selected',i===j);b.tabIndex=i===j?0:-1});ps.forEach(function(p,i){p.classList.toggle('is-on',i===j);p.setAttribute('aria-hidden',i!==j)});var b=bs[j];bar.style.width=b.offsetWidth+'px';bar.style.transform='translateX('+b.offsetLeft+'px)';r.dataset.k=j%4;if(f)b.focus()}
 bs.forEach(function(b,i){b.addEventListener('click',function(){set(i)});b.addEventListener('keydown',function(e){var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(d){e.preventDefault();set((i+d+bs.length)%bs.length,1)}})});
 window.addEventListener('resize',function(){set(k)});set(0)});},
  /* CopyButton */ function(Q){Q('.ix-cp').forEach(function(r){var b=r.querySelector('button'),l=b.querySelector('.l'),txt=r.querySelector('span').textContent,t;
 b.addEventListener('click',function(){try{if(navigator.clipboard)navigator.clipboard.writeText(txt).catch(function(){})}catch(e){}b.classList.add('is-done');l.textContent='Copied';clearTimeout(t);t=setTimeout(function(){b.classList.remove('is-done');l.textContent='Copy link'},1600)})});},
  /* InlineEdit */ function(Q){Q('.ix-ie').forEach(function(r){var t=r.querySelector('.ix-ie-t'),txt=t.querySelector('span'),s=r.querySelector('.ix-ie-s'),tm;
 t.addEventListener('click',function(){var inp=document.createElement('input'),done=false;inp.value=txt.textContent;inp.setAttribute('aria-label','Title');t.hidden=true;r.insertBefore(inp,t);inp.focus();inp.select();
  function fin(save,back){if(done)return;done=true;var v=inp.value.trim();if(save&&v&&v!==txt.textContent){txt.textContent=v;s.classList.add('is-on');clearTimeout(tm);tm=setTimeout(function(){s.classList.remove('is-on')},1800)}inp.remove();t.hidden=false;if(back)t.focus()}
  inp.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();fin(true,1)}else if(e.key==='Escape'){e.preventDefault();fin(false,1)}});inp.addEventListener('blur',function(){fin(true,0)})})});},
  /* TagInput */ function(Q){Q('.ix-tg').forEach(function(r){var inp=r.querySelector('input'),live=r.parentNode.querySelector('.ix-live');
 function tags(){return [].slice.call(r.querySelectorAll(':scope > span'))}
 function say(){var n=tags().length;if(live)live.textContent=n+(n===1?' tag':' tags')}
 function add(v){v=v.replace(/,/g,'').trim();inp.value='';if(!v)return;if(tags().some(function(s){return s.firstChild.textContent.toLowerCase()===v.toLowerCase()}))return;var s=document.createElement('span');s.appendChild(document.createTextNode(v));s.insertAdjacentHTML('beforeend','<button type="button">'+IXX+'</button>');s.querySelector('button').setAttribute('aria-label','Remove '+v);r.insertBefore(s,inp);say()}
 r.addEventListener('click',function(e){var b=e.target.closest('span > button');if(b){b.parentNode.remove();say();inp.focus();return}if(e.target===r)inp.focus()});
 inp.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===','){e.preventDefault();add(inp.value)}else if(e.key==='Backspace'&&!inp.value){var ts=tags();if(ts.length){ts[ts.length-1].remove();say()}}})});},
  /* PointerSpotlight */ function(Q){Q('.ix-sp').forEach(function(g){var ts=[].slice.call(g.children);function mv(e){ts.forEach(function(t){var b=t.getBoundingClientRect();t.style.setProperty('--x',(e.clientX-b.left)+'px');t.style.setProperty('--y',(e.clientY-b.top)+'px')});g.classList.add('is-on')}
 g.addEventListener('pointermove',mv);g.addEventListener('pointerdown',mv);g.addEventListener('pointerleave',function(){g.classList.remove('is-on')})});},
  /* TiltCard */ function(Q){Q('.ix-tl').forEach(function(w){if(RM)return;var c=w.querySelector('.ix-tl-c');
 w.addEventListener('pointermove',function(e){var b=c.getBoundingClientRect(),x=Math.max(0,Math.min(1,(e.clientX-b.left)/b.width)),y=Math.max(0,Math.min(1,(e.clientY-b.top)/b.height));c.classList.add('is-move');c.style.setProperty('--ry',((x-.5)*16).toFixed(2)+'deg');c.style.setProperty('--rx',((.5-y)*16).toFixed(2)+'deg');c.style.setProperty('--sx',(x*100)+'%');c.style.setProperty('--sy',(y*100)+'%')});
 w.addEventListener('pointerleave',function(){c.classList.remove('is-move');c.style.setProperty('--rx','0deg');c.style.setProperty('--ry','0deg')})});},
  /* FlipCards */ function(Q){Q('.ix-fl button').forEach(function(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true')})});},
  /* WordRise */ function(Q){Q('.ix-wrw').forEach(function(r){var w=r.querySelector('.ix-wr'),p=w.querySelector('p');p.setAttribute('aria-label',p.textContent);p.innerHTML=p.textContent.split(' ').map(function(x,j){return '<span aria-hidden="true"><i style="--k:'+j+'">'+x+'</i></span>'}).join(' ');
 function run(){w.classList.add('is-reset');w.classList.remove('is-on');void w.offsetWidth;w.classList.remove('is-reset');requestAnimationFrame(function(){requestAnimationFrame(function(){w.classList.add('is-on')})})}
 var rp=r.querySelector('[data-replay]');if(rp)rp.addEventListener('click',run);ixView(r,function(){w.classList.add('is-on')})});},
  /* MagneticButton */ function(Q){Q('.ix-mg').forEach(function(w){if(RM)return;
 w.addEventListener('pointermove',function(e){var b=w.getBoundingClientRect(),dx=e.clientX-(b.left+b.width/2),dy=e.clientY-(b.top+b.height/2);w.classList.add('is-move');w.style.setProperty('--mx',Math.max(-22,Math.min(22,dx*.3)).toFixed(1)+'px');w.style.setProperty('--my',Math.max(-14,Math.min(14,dy*.3)).toFixed(1)+'px')});
 w.addEventListener('pointerleave',function(){w.classList.remove('is-move');w.style.setProperty('--mx','0px');w.style.setProperty('--my','0px')})});},
  /* PinnedProcess: the held side swaps to the step nearest the top of the frame */ function(Q){Q('.br-proc').forEach(function(box){var steps=[].slice.call(box.querySelectorAll('.br-proc-step')),hold=box.querySelector('.br-proc-hold'),title=hold&&hold.querySelector('p'),detail=hold&&hold.querySelector('small'),pic=hold&&hold.querySelector('.br-proc-pic'),cur=-1;if(!steps.length||!hold)return;
 function show(k){if(k===cur)return;cur=k;steps.forEach(function(s,j){s.classList.toggle('is-on',j===k)});var s=steps[k],cs=getComputedStyle(s);hold.style.setProperty('--hold',cs.getPropertyValue('--st'));hold.style.setProperty('--hold-soft',cs.getPropertyValue('--st-soft'));if(title&&s.dataset.title)title.textContent=s.dataset.title;if(detail&&s.dataset.detail)detail.textContent=s.dataset.detail;if(pic&&s.dataset.image)pic.style.backgroundImage='url('+s.dataset.image+')'}
 function upd(){var top=box.scrollTop,best=0;steps.forEach(function(s,j){if(s.offsetTop-box.offsetTop<=top+40)best=j});if(box.scrollTop+box.clientHeight>=box.scrollHeight-4)best=steps.length-1;show(best)}
 box.addEventListener('scroll',upd);upd()});}
];
function init(root){root=root||document;inits.forEach(function(f,i){try{f(function(sel){return fresh(root,sel,i)})}catch(e){if(window.console)console.error(e)}})}
window.LLCInteractions={init:init};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){init()});else init();
})();
(function () {
  var React = window.React, h = React.createElement, useState = React.useState;
  var ICONS = {"home": "<path d=\"M4 11 12 4l8 7v8.5a1 1 0 0 1-1 1h-4.5V15h-5v5.5H5a1 1 0 0 1-1-1V11Z\"></path>", "kanban": "<rect x=\"3.5\" y=\"4.5\" width=\"17\" height=\"15\" rx=\"2\"></rect><path d=\"M8 8v5\"></path><path d=\"M12 8v8\"></path><path d=\"M16 8v3\"></path>", "briefcase": "<rect x=\"3.5\" y=\"8\" width=\"17\" height=\"12\" rx=\"2\"></rect><path d=\"M8.5 8V6a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v2\"></path><path d=\"M3.5 13h17\"></path>", "users": "<circle cx=\"9\" cy=\"8\" r=\"3.5\"></circle><path d=\"M2.5 19.5a6.5 6.5 0 0 1 13 0\"></path><path d=\"M16 4.8a3.5 3.5 0 0 1 0 6.4\"></path><path d=\"M18 14.3a6.5 6.5 0 0 1 3.5 5.2\"></path>", "inbox": "<path d=\"M4 13h4l1.5 2.5h5L16 13h4\"></path><path d=\"M5.5 5h13l1.5 8v5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18v-5l1.5-8Z\"></path>", "calendar": "<rect x=\"3.5\" y=\"5\" width=\"17\" height=\"15.5\" rx=\"2\"></rect><path d=\"M3.5 10h17\"></path><path d=\"M8 3v4\"></path><path d=\"M16 3v4\"></path>", "chart-bar": "<path d=\"M4 20h16\"></path><path d=\"M7 16v-5\"></path><path d=\"M12 16V6\"></path><path d=\"M17 16V9\"></path>", "settings": "<circle cx=\"12\" cy=\"12\" r=\"3\"></circle><path d=\"M12 2.5v3\"></path><path d=\"M12 18.5v3\"></path><path d=\"M2.5 12h3\"></path><path d=\"M18.5 12h3\"></path><path d=\"m5.3 5.3 2.1 2.1\"></path><path d=\"m16.6 16.6 2.1 2.1\"></path><path d=\"m5.3 18.7 2.1-2.1\"></path><path d=\"m16.6 7.4 2.1-2.1\"></path>", "search": "<circle cx=\"11\" cy=\"11\" r=\"7\"></circle><path d=\"m20 20-3.5-3.5\"></path>", "plus": "<path d=\"M12 5v14\"></path><path d=\"M5 12h14\"></path>", "check": "<path d=\"m5 12 5 5 9-10\"></path>", "close": "<path d=\"M6 6l12 12\"></path><path d=\"M18 6 6 18\"></path>", "more": "<circle cx=\"5\" cy=\"12\" r=\"1\"></circle><circle cx=\"12\" cy=\"12\" r=\"1\"></circle><circle cx=\"19\" cy=\"12\" r=\"1\"></circle>", "chevron-down": "<path d=\"m6 9 6 6 6-6\"></path>", "chevron-right": "<path d=\"m9 6 6 6-6 6\"></path>", "chevron-left": "<path d=\"m15 6-6 6 6 6\"></path>", "sparkles": "<path d=\"M11 4c.6 3.8 2.2 5.4 6 6-3.8.6-5.4 2.2-6 6-.6-3.8-2.2-5.4-6-6 3.8-.6 5.4-2.2 6-6Z\"></path><path d=\"M18.5 15.5v5\"></path><path d=\"M16 18h5\"></path>", "send": "<path d=\"M20.5 3.5 3.5 10l7 3.5 3.5 7 6.5-17Z\"></path><path d=\"m10.5 13.5 4-4\"></path>", "file-text": "<path d=\"M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z\"></path><path d=\"M14 3v5h5\"></path><path d=\"M8.5 13h7\"></path><path d=\"M8.5 16.5h7\"></path>", "clock": "<circle cx=\"12\" cy=\"12\" r=\"8.5\"></circle><path d=\"M12 7.5V12l3 2\"></path>", "trending-up": "<path d=\"m3.5 17 6-6 4 4 7-7.5\"></path><path d=\"M15.5 7.5h5v5\"></path>", "moon": "<path d=\"M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z\"></path>", "sun": "<circle cx=\"12\" cy=\"12\" r=\"4\"></circle><path d=\"M12 2.5V5\"></path><path d=\"M12 19v2.5\"></path><path d=\"M2.5 12H5\"></path><path d=\"M19 12h2.5\"></path><path d=\"m5.3 5.3 1.8 1.8\"></path><path d=\"m16.9 16.9 1.8 1.8\"></path><path d=\"m5.3 18.7 1.8-1.8\"></path><path d=\"m16.9 7.1 1.8-1.8\"></path>"};
  function cx() { return Array.prototype.filter.call(arguments, Boolean).join(' '); }
  function Icon(p) {
    return h('svg', { className: p.gradient ? 'mer-icon llc-icon-grad' : 'mer-icon', width: p.size || 18, height: p.size || 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true, dangerouslySetInnerHTML: { __html: ICONS[p.name] || '' } });
  }
  function Logo(p) {
    var s = p.size || 28;
    var pill = h('span', { className: 'llc-code-pill llc-logo-pill', style: { fontSize: Math.round(s * 0.55) + 'px' }, 'aria-hidden': true }, 'Code', h('span', { className: 'llc-cursor' }, '_'));
    if (p.markOnly) return h('span', { className: 'mer-logo llc-logo', role: 'img', 'aria-label': 'LiveLaughCode' }, pill);
    return h('span', { className: 'mer-logo llc-logo', role: 'img', 'aria-label': 'Live, Laugh, Code' }, h('span', { className: 'llc-serif', style: { fontSize: Math.round(s * 1.24) + 'px' }, 'aria-hidden': true }, 'Live, Laugh,'), pill);
  }
  function Button(p) {
    var v = p.variant || 'primary';
    var cls = cx('mer-btn', 'mer-btn-' + v, p.size === 'sm' && 'mer-btn-sm');
    var kids = [p.loading ? h('i', { key: 'l', className: 'mer-spinner', 'aria-hidden': true }) : p.icon ? h(Icon, { key: 'i', name: p.icon, size: 16 }) : null, h('span', { key: 't' }, p.children)];
    return p.href ? h('a', { className: cls, href: p.href }, kids) : h('button', { className: cls, type: p.type || 'button', disabled: p.disabled || p.loading, 'aria-busy': p.loading || undefined, onClick: p.onClick }, kids);
  }
  function IconButton(p) { return h('button', { className: cx('mer-iconbtn', p.size === 'sm' && 'mer-iconbtn-sm'), type: 'button', 'aria-label': p.label, title: p.label, onClick: p.onClick }, h(Icon, { name: p.icon, size: p.size === 'sm' ? 16 : 18 })); }
  // Tag names what kind of thing a record is. It never carries state.
  function Tag(p) { return h('span', { className: 'mer-tag' }, p.children); }
  // StateText says where something stands in plain words. Weight, not hue, marks what needs a person.
  // status adds the shaped marker: draft, review, approved or blocked. The word still carries the meaning.
  function StateText(p) {
    return h('span', { className: cx('mer-state', p.attention && 'is-attention', p.status && 'has-mark') }, p.status ? h('i', { className: 'br-mark', 'data-status': p.status, 'aria-hidden': true }) : null, h('span', { className: 'mer-state-word' }, p.children), p.reason ? h('span', { className: 'mer-state-reason' }, p.reason) : null);
  }
  function Avatar(p) {
    var i = p.name.split(' ').map(function (w) { return w[0]; }).slice(0, 2).join('');
    var k = 0; for (var j = 0; j < p.name.length; j++) k = (k + p.name.charCodeAt(j)) % 4;
    var a = h('span', { className: cx('mer-avatar', 'mer-avatar-t' + k, p.size === 'sm' && 'mer-avatar-sm'), title: p.name, 'aria-label': p.withName ? undefined : p.name, 'aria-hidden': p.withName ? true : undefined, role: p.withName ? undefined : 'img' }, i);
    return p.withName ? h('span', { className: 'mer-person' }, a, p.name) : a;
  }
  function Field(p) {
    var as = p.as || 'input';
    return h('label', { className: 'mer-field' }, h('span', { className: 'mer-field-label' }, p.label, p.required ? h('span', { className: 'mer-field-req' }, ' required') : null),
      (function () { var ctl = h(as, { defaultValue: p.defaultValue, placeholder: p.placeholder, disabled: p.disabled, readOnly: p.readOnly, required: p.required, 'aria-invalid': p.error ? true : undefined }, as === 'select' ? (p.options || []).map(function (o) { return h('option', { key: o }, o); }) : undefined);
        return as === 'select' ? h('span', { className: 'mer-select' }, ctl, h(Icon, { name: 'chevron-down', size: 16 })) : ctl; })(),
      p.error ? h('span', { className: 'mer-field-error' }, p.error) : p.hint ? h('span', { className: 'mer-field-hint' }, p.hint) : null);
  }
  function Search(p) {
    return h('label', { className: 'mer-search' }, h(Icon, { name: 'search', size: 16 }),
      h('input', { 'aria-label': p.label || 'Search', placeholder: p.placeholder || 'Search', defaultValue: p.defaultValue }),
      p.shortcut ? h('kbd', { 'aria-hidden': true }, p.shortcut) : null);
  }
  function Checkbox(p) {
    var st = useState(!!p.defaultChecked);
    return h('label', { className: 'mer-check' }, h('input', { type: 'checkbox', checked: st[0], onChange: function (e) { st[1](e.target.checked); } }),
      h('span', { className: 'mer-check-box', 'aria-hidden': true }, st[0] ? h(Icon, { name: 'check', size: 14 }) : null), p.label);
  }
  function Toggle(p) {
    var st = useState(!!p.defaultChecked);
    return h('button', { className: 'mer-toggle', type: 'button', role: 'switch', 'aria-checked': st[0], onClick: function () { st[1](!st[0]); } }, h('span', { className: 'mer-toggle-track', 'aria-hidden': true }, h('span', null)), p.label);
  }
  function Tabs(p) {
    var st = useState(p.defaultValue || p.items[0].label);
    return h('div', { className: 'mer-tabs', role: 'tablist' }, p.items.map(function (t) {
      var on = t.label === st[0];
      return h('button', { key: t.label, type: 'button', role: 'tab', 'aria-selected': on, onClick: function () { st[1](t.label); } }, t.label);
    }));
  }
  function Segmented(p) {
    var st = useState(p.defaultValue || p.items[0]);
    return h('div', { className: 'mer-seg', role: 'group', 'aria-label': p.label }, p.items.map(function (t) {
      return h('button', { key: t, type: 'button', 'aria-pressed': t === st[0], onClick: function () { st[1](t); } }, t);
    }));
  }
  // Breadcrumb: the full trail, never folded. Items are strings or { label, href }; the last is the current page.
  function Breadcrumb(p) {
    return h('nav', { className: 'br-bc', 'aria-label': p.label || 'Breadcrumb' }, h('ol', null, p.items.map(function (it, i) {
      var o = typeof it === 'string' ? { label: it } : it, last = i === p.items.length - 1;
      return h('li', { key: i }, last ? h('span', { 'aria-current': 'page' }, o.label) : h('a', { href: o.href || '#' }, o.label));
    })));
  }
  function Pagination(p) {
    var st = useState(p.page || 1), n = [];
    for (var i = 1; i <= p.pages; i++) n.push(i);
    return h('nav', { className: 'mer-pages', 'aria-label': 'Pages' },
      h(IconButton, { icon: 'chevron-left', label: 'Previous page', size: 'sm', onClick: function () { st[1](Math.max(1, st[0] - 1)); } }),
      n.map(function (i) { return h('button', { key: i, type: 'button', 'aria-current': i === st[0] ? 'page' : undefined, onClick: function () { st[1](i); } }, i); }),
      h(IconButton, { icon: 'chevron-right', label: 'Next page', size: 'sm', onClick: function () { st[1](Math.min(p.pages, st[0] + 1)); } }));
  }
  function Card(p) {
    return h('section', { className: cx('mer-card', p.flush && 'mer-card-flush') }, p.title ? h('header', null, h('div', null, h('h3', null, p.title), p.subtitle ? h('p', null, p.subtitle) : null), p.action || null) : null, p.children);
  }
  function Metric(p) {
    return h('div', { className: 'mer-metric' }, h('span', null, p.label), h('strong', null, p.value),
      p.note ? h('small', null, p.note) : null);
  }
  // FactBand: the four or so facts that answer a screen's question, read left to right.
  function FactBand(p) {
    return h('dl', { className: 'mer-facts' }, p.facts.map(function (f) {
      return h('div', { key: f.label, className: 'mer-fact' }, h('dt', null, f.label), h('dd', null, h('strong', null, f.value), f.note ? h('span', null, f.note) : null));
    }));
  }
  // DataTable: rows, optionally grouped. Group order carries urgency; quiet rows step back.
  function DataTable(p) {
    var st = useState(p.selected == null ? null : p.selected);
    var cols = p.columns;
    function row(r, key) {
      var on = p.selectable && st[0] === r.id;
      return h('tr', { key: key, className: cx(r.quiet && 'is-quiet', on && 'is-selected'), 'aria-selected': p.selectable ? !!on : undefined, onClick: p.selectable ? function () { st[1](r.id); } : undefined },
        cols.map(function (c, ci) {
          var v = r[c.key];
          var body = ci === 0 && r.sub ? [h('span', { key: 'v', className: 'mer-cell-main' }, v), h('span', { key: 's', className: 'mer-cell-sub' }, r.sub)] : v;
          return h(ci === 0 ? 'th' : 'td', { key: c.key, scope: ci === 0 ? 'row' : undefined, className: c.numeric ? 'mer-num' : undefined }, body);
        }));
    }
    var bodies = p.groups ? p.groups.map(function (g, gi) {
      return h('tbody', { key: g.label }, h('tr', { className: 'mer-group' }, h('th', { colSpan: cols.length, scope: 'rowgroup' }, g.label, h('span', null, g.rows.length), g.note ? h('em', null, g.note) : null)),
        g.rows.map(function (r, i) { return row(r, gi + '-' + i); }));
    }) : h('tbody', null, p.rows.map(function (r, i) { return row(r, i); }));
    return h('div', { className: 'mer-table-wrap' }, h('table', { className: cx('mer-table', p.selectable && 'is-selectable') },
      p.caption ? h('caption', null, p.caption) : null,
      h('thead', null, h('tr', null, cols.map(function (c) { return h('th', { key: c.key, scope: 'col', className: c.numeric ? 'mer-num' : undefined, style: c.width ? { width: c.width } : undefined }, c.label); }))),
      bodies));
  }
  // RecordRow: one fact, finding or document with where it came from and the one thing to do about it.
  function RecordRow(p) {
    return h('div', { className: cx('mer-record', p.attention && 'is-attention', !p.state && 'no-state') },
      p.state ? h('span', { className: 'mer-record-state' }, p.state) : null,
      h('div', { className: 'mer-record-body' }, h('p', { className: 'mer-record-title' }, p.title), p.source ? h('p', { className: 'mer-record-source' }, p.source) : null),
      p.action ? h('div', { className: 'mer-record-action' }, p.action) : null);
  }
  // DetailPanel: the side panel for whatever is selected, in labeled sections of short rows.
  function DetailPanel(p) {
    return h('aside', { className: 'mer-detail', 'aria-label': p.kicker || 'Selected item' },
      p.kicker ? h('p', { className: 'mer-detail-kicker' }, p.kicker) : null,
      h('h3', null, p.title), p.subtitle ? h('p', { className: 'mer-detail-sub' }, p.subtitle) : null,
      p.sections.map(function (s) {
        return h('section', { key: s.label }, h('h4', null, s.label), h('dl', null, s.rows.map(function (r, i) {
          return h('div', { key: i, className: cx('mer-kv', r.attention && 'is-attention') }, h('dt', null, r.label), h('dd', null, r.value), r.source ? h('p', null, r.source) : null);
        })));
      }), p.children || null);
  }
  function Timeline(p) {
    return h('ol', { className: 'mer-timeline' }, p.items.map(function (it, i) {
      return h('li', { key: i, className: it.now ? 'is-now' : undefined }, h('span', { className: 'mer-when' }, it.when), h('div', null, h('p', { className: 'mer-record-title' }, it.title), it.detail ? h('p', { className: 'mer-record-source' }, it.detail) : null));
    }));
  }
  // DecisionList: ranked by what each item unblocks; one opens at a time to show why and the action.
  function DecisionList(p) {
    var st = useState(p.defaultOpen == null ? 0 : p.defaultOpen);
    return h('ol', { className: 'mer-decisions' }, p.items.map(function (it, i) {
      var open = st[0] === i;
      return h('li', { key: i, className: open ? 'is-open' : undefined },
        h('button', { type: 'button', 'aria-expanded': open, onClick: function () { st[1](open ? -1 : i); } },
          h('span', { className: 'mer-rank' }, i + 1),
          h('span', { className: 'mer-decision-text' }, h('span', { className: 'mer-record-title' }, it.title), h('span', { className: 'mer-record-source' }, it.unblocks)),
          h(Icon, { name: open ? 'chevron-down' : 'chevron-right', size: 16 })),
        open ? h('div', { className: 'mer-decision-why' }, h('p', null, it.why), it.action ? h(Button, { size: 'sm' }, it.action) : null) : null);
    }));
  }
  // WeekStrip: five working days; your items are buttons, other people's are dashed notes.
  function WeekStrip(p) {
    var st = useState(p.defaultSelected || null);
    return h('div', { className: 'mer-week', role: 'group', 'aria-label': p.label || 'This week' }, p.days.map(function (d) {
      var empty = !(d.items || []).length && !(d.others || []).length;
      return h('div', { key: d.label, className: cx('mer-day', d.today && 'is-today') },
        h('p', { className: 'mer-day-head' }, h('span', null, d.label), d.tag ? h('b', null, d.tag) : null),
        (d.items || []).map(function (it) {
          return h('button', { key: it.id, type: 'button', className: cx('mer-chip', it.late && 'is-late'), 'aria-pressed': st[0] === it.id, onClick: function () { st[1](st[0] === it.id ? null : it.id); } }, it.label);
        }),
        (d.others || []).map(function (o) { return h('p', { key: o, className: 'mer-chip-other' }, o); }),
        empty ? h('p', { className: 'mer-day-none' }, 'Nothing due') : null);
    }));
  }
  function DealBoard(p) {
    return h('div', { className: 'mer-board' }, p.columns.map(function (c) {
      return h('section', { key: c.title, className: cx('mer-col', c.current && 'is-now') },
        h('header', null, h('span', null, c.title), h('span', { className: 'mer-count' }, c.deals.length)),
        c.deals.map(function (d) {
          return h('article', { key: d.name, className: cx('mer-deal', d.attention && 'is-attention'), tabIndex: 0 }, h('strong', null, d.name), d.value ? h('span', { className: 'mer-deal-value' }, d.value) : null,
            d.next ? h('p', { className: 'mer-deal-next' }, d.next) : null,
            h('footer', null, h(Avatar, { name: d.owner, size: 'sm', withName: true })));
        }), c.deals.length ? null : h('p', { className: 'mer-col-none' }, 'No deals in ' + c.title));
    }));
  }
  function StageSpine(p) {
    return h('nav', { className: 'mer-spine', 'aria-label': p.label || 'Deal stages' }, h('ol', null, p.stages.map(function (s, i) {
      var done = i < p.current, cur = i === p.current;
      return h('li', { key: s, className: cx(done && 'is-done', cur && 'is-now') },
        h('a', { href: '#', 'aria-current': cur ? 'step' : undefined }, h('i', { 'aria-hidden': true }, done ? h(Icon, { name: 'check', size: 12 }) : null), s));
    })));
  }
  function ColumnChart(p) {
    var max = 0;
    p.groups.forEach(function (g) { g.values.forEach(function (v) { max = Math.max(max, v); }); });
    return h('figure', { className: 'mer-chart' },
      h('div', { className: 'mer-chart-plot', role: 'img', 'aria-label': p.label }, p.groups.map(function (g, gi) {
        return h('div', { key: g.label, className: cx('mer-chart-group', gi === p.now && 'is-now') },
          h('div', { className: 'mer-chart-bars' }, g.values.map(function (v, i) { return h('span', { key: i, title: p.series[i] + ': ' + v, style: { height: (v / max * 100) + '%', background: 'var(--chart-' + (i + 1) + ')' } }); })),
          h('em', null, g.label));
      })),
      h('figcaption', null, p.series.map(function (s, i) { return h('span', { key: s }, h('i', { style: { background: 'var(--chart-' + (i + 1) + ')' } }), s); })));
  }
  function EmptyState(p) {
    return h('div', { className: 'mer-empty' }, h('p', { className: 'mer-empty-title' }, p.title), p.children ? h('p', null, p.children) : null, p.action || null);
  }
  function Sidebar(p) {
    return h('nav', { className: 'mer-sidebar', 'aria-label': 'Main' }, h('div', { className: 'mer-sidebar-brand' }, h(Logo, null)),
      h('div', { className: 'mer-sidebar-body' }, p.groups.map(function (g, gi) {
        return h('div', { className: 'mer-sidebar-group', key: gi }, g.label ? h('p', null, g.label) : null, g.items.map(function (it) {
          return h('a', { key: it.label, href: '#', 'aria-current': it.current ? 'page' : undefined }, it.icon ? h(Icon, { name: it.icon, size: 18 }) : h('i', { className: 'mer-pin', 'aria-hidden': true }), h('span', null, it.label), it.kind ? h('small', null, it.kind) : it.count != null ? h('span', { className: 'mer-count' }, it.count) : null);
        }));
      })),
      p.user ? h('div', { className: 'mer-sidebar-user' }, h(Avatar, { name: p.user.name }), h('div', null, h('strong', null, p.user.name), h('span', null, p.user.role))) : null);
  }
  function TopBar(p) {
    return h('header', { className: 'mer-topbar' }, h('div', { className: 'mer-topbar-lead' }, p.lead), h('div', { className: 'mer-topbar-end' }, p.children));
  }
  function Conversation(p) {
    return h('aside', { className: 'mer-convo' },
      h('header', null, h(Icon, { name: 'sparkles', size: 18 }), h('h3', null, p.title)),
      h('div', { className: 'mer-convo-list' }, p.messages.map(function (m, i) { return h('div', { key: i, className: cx('mer-msg', m.user && 'mer-msg-user') }, m.text, m.source ? h('span', { className: 'mer-msg-source' }, m.source) : null); })),
      p.suggestions ? h('div', { className: 'mer-convo-chips' }, p.suggestions.map(function (s) { return h('button', { key: s, type: 'button' }, s); })) : null,
      h('form', { className: 'mer-composer', onSubmit: function (e) { e.preventDefault(); } },
        h('input', { 'aria-label': 'Message', placeholder: p.placeholder || 'Ask about this account' }),
        h('button', { type: 'submit', 'aria-label': 'Send' }, h(Icon, { name: 'send', size: 16 }))));
  }
  function Dialog(p) {
    return h('div', { className: 'mer-scrim' }, h('div', { className: 'mer-dialog', role: 'dialog', 'aria-modal': true, 'aria-label': p.title }, h('h2', null, p.title), h('p', null, p.children), h('footer', null, p.actions)));
  }
  function Toast(p) {
    return h('div', { className: 'mer-toast', role: 'status' }, h(Icon, { name: 'check', size: 16 }), h('span', null, p.children), p.action ? h('button', { type: 'button' }, p.action) : null);
  }

  // ---------- added in version 17 ----------
  function Tooltip(p) {
    var s = useState(false), open = p.open || s[0];
    return h('span', { className: 'mer-tip', onMouseEnter: function () { s[1](true); }, onMouseLeave: function () { s[1](false); }, onFocus: function () { s[1](true); }, onBlur: function () { s[1](false); } },
      p.children, open ? h('span', { className: 'mer-tip-box', role: 'tooltip' }, p.text) : null);
  }
  function Menu(p) {
    var s = useState(!!p.defaultOpen);
    return h('div', { className: 'mer-menu' },
      h('button', { type: 'button', className: 'mer-btn mer-btn-secondary mer-btn-sm', 'aria-haspopup': 'menu', 'aria-expanded': s[0], onClick: function () { s[1](!s[0]); } }, h('span', null, p.label), h(Icon, { name: 'chevron-down', size: 16 })),
      s[0] ? h('div', { className: 'mer-menu-list', role: 'menu' }, p.items.map(function (it, i) {
        if (it.divider) return h('hr', { key: i });
        return h('button', { key: i, type: 'button', role: 'menuitem', className: cx(it.danger && 'is-danger'), disabled: it.disabled },
          it.icon ? h(Icon, { name: it.icon, size: 16 }) : h('i', { className: 'mer-menu-gap' }), h('span', null, h('b', null, it.label), it.hint ? h('small', null, it.hint) : null), it.shortcut ? h('kbd', null, it.shortcut) : null);
      })) : null);
  }
  function FilterBar(p) {
    return h('div', { className: 'mer-filters', role: 'group', 'aria-label': p.label || 'Filters' },
      p.search ? h('label', { className: 'mer-filters-search' }, h(Icon, { name: 'search', size: 16 }), h('input', { 'aria-label': p.search, placeholder: p.search })) : null,
      (p.filters || []).map(function (f) {
        return h('button', { key: f.label, type: 'button', className: cx('mer-filter', f.set && 'is-set'), 'aria-pressed': f.set ? true : undefined }, h('span', null, f.label), h('b', null, f.value || 'Any'), h(Icon, { name: 'chevron-down', size: 14 }));
      }),
      p.clearable ? h('button', { type: 'button', className: 'mer-filters-clear' }, 'Clear filters') : null,
      h('span', { className: 'mer-filters-count', 'aria-live': 'polite' }, p.count),
      p.sort ? h('button', { type: 'button', className: 'mer-filter mer-filter-sort' }, h('span', null, 'Order'), h('b', null, p.sort), h(Icon, { name: 'chevron-down', size: 14 })) : null);
  }
  function Skeleton(p) {
    var n = p.rows || 4;
    return h('div', { className: 'mer-skeleton', 'aria-busy': true, 'aria-label': p.label || 'Loading' },
      h('span', { className: 'mer-sr' }, p.label || 'Loading'),
      Array.apply(null, Array(n)).map(function (_, i) { return h('div', { key: i, className: 'mer-skeleton-row', 'aria-hidden': true }, h('i', { style: { width: (62 - i * 9 % 30) + '%' } }), h('i', { style: { width: (38 + i * 13 % 24) + '%' } })); }));
  }
  function Progress(p) {
    var pct = Math.max(0, Math.min(100, Math.round(p.value / p.max * 100)));
    return h('div', { className: 'mer-progress' },
      h('div', { className: 'mer-progress-head' }, h('span', null, p.label), h('strong', null, p.value + (p.unit || '') + ' of ' + p.max + (p.unit || ''))),
      h('div', { className: 'mer-progress-track', role: 'progressbar', 'aria-label': p.label, 'aria-valuenow': p.value, 'aria-valuemin': 0, 'aria-valuemax': p.max },
        h('span', { style: { width: pct + '%' } }), p.expected != null ? h('i', { style: { left: Math.round(p.expected / p.max * 100) + '%' }, title: 'Planned by now: ' + p.expected + (p.unit || '') }) : null),
      p.note ? h('p', { className: 'mer-progress-note' }, p.note) : null);
  }
  function Callout(p) {
    return h('div', { className: 'mer-callout', role: 'note' },
      h(Icon, { name: p.icon || 'sparkles', size: 18 }),
      h('div', { className: 'mer-callout-body' }, h('p', { className: 'mer-callout-title' }, p.title), p.children ? h('p', null, p.children) : null, p.source ? h('p', { className: 'mer-callout-source' }, p.source) : null),
      p.action ? h('div', { className: 'mer-callout-action' }, p.action) : null);
  }
  function ProposedChange(p) {
    return h('section', { className: cx('mer-proposal', p.confirmed && 'is-confirmed'), 'aria-label': 'Proposed change: ' + p.title },
      h('header', null, h(Icon, { name: p.confirmed ? 'check' : 'sparkles', size: 16 }), h('span', null, p.confirmed ? (p.confirmedBy || 'Confirmed') : (p.kicker || 'Proposed, your call'))),
      h('div', { className: 'mer-proposal-body' },
        h('p', { className: 'mer-proposal-title' }, p.title),
        p.from != null ? h('p', { className: 'mer-delta' }, h('del', null, p.from), h(Icon, { name: 'chevron-right', size: 14 }), h('ins', null, p.to)) : null,
        p.children ? h('p', { className: 'mer-proposal-why' }, p.children) : null,
        p.source ? h('p', { className: 'mer-proposal-source' }, p.source) : null),
      p.confirmed ? null : h('footer', null, h(Button, { size: 'sm', icon: 'check' }, p.confirmLabel || 'Confirm'), h(Button, { size: 'sm', variant: 'secondary' }, 'Edit'), h(Button, { size: 'sm', variant: 'ghost' }, 'Set aside'), p.note ? h('span', null, p.note) : null));
  }
  function Grounds(p) {
    return h('div', { className: 'mer-grounds' }, h('p', { className: 'mer-grounds-label' }, p.label || 'What this rests on'),
      h('dl', null, p.items.map(function (it, i) {
        return h('div', { key: i }, h('dt', null, it.kind), h('dd', null, it.text, it.source ? h('span', null, it.source) : null));
      })));
  }
  function Quote(p) {
    return h('figure', { className: 'mer-quote' }, h('blockquote', null, p.children), p.source ? h('figcaption', null, p.source) : null);
  }
  function AgentActivity(p) {
    var tones = ['a', 'b', 'c', 'd'];
    function tone(n) { var s = 0; for (var i = 0; i < n.length; i++) s = (s * 31 + n.charCodeAt(i)) % 997; return tones[s % tones.length]; }
    var live = p.items.filter(function (x) { return x.live; }).length;
    return h('section', { className: 'mer-agents', 'aria-label': p.title || 'Agent activity' },
      h('header', null, h('p', null, p.title || 'Agent activity'), live ? h('span', { className: 'mer-agents-live' }, h('i', { 'aria-hidden': true }), live + ' working now') : null),
      h('ol', null, p.items.map(function (it, i) {
        return h('li', { key: i, className: cx('mer-agent', it.live && 'is-live') },
          h('span', { className: 'mer-agent-face is-' + tone(it.agent), 'aria-hidden': true }, it.agent.slice(0, 2)),
          h('div', { className: 'mer-agent-body' },
            h('p', { className: 'mer-agent-head' }, h('b', null, it.agent), h('span', null, it.live ? 'Working now' : it.when)),
            h('p', { className: 'mer-agent-text' }, it.text),
            it.live ? h('span', { className: 'mer-agent-bar', 'aria-hidden': true }, h('i')) : null));
      })));
  }
  function SectionChanges(p) {
    var s = useState(p.defaultOpen != null ? p.defaultOpen : (p.items.findIndex ? p.items.findIndex(function (x) { return x.changed; }) : 0));
    return h('div', { className: 'mer-sections' }, p.summary ? h('p', { className: 'mer-sections-summary' }, p.summary) : null,
      h('ol', null, p.items.map(function (it, i) {
        var open = s[0] === i && it.detail;
        return h('li', { key: i, className: cx(it.changed && 'is-changed', open && 'is-open') },
          h('button', { type: 'button', 'aria-expanded': it.detail ? !!open : undefined, onClick: function () { s[1](open ? -1 : i); } },
            h('span', { className: 'mer-sections-n' }, it.n), h('span', { className: 'mer-sections-t' }, it.title), h('span', { className: 'mer-sections-c' }, it.change)),
          open ? h('div', { className: 'mer-sections-detail' }, h('p', null, it.detail), it.source ? h('p', { className: 'mer-sections-src' }, it.source) : null) : null);
      })));
  }

  // ---------- added 17 November: approved Gallery behaviour ----------
  var STATUS_WORDS = { draft: 'Draft', review: 'In review', approved: 'Approved', blocked: 'Blocked' };
  // StatusBadge: a shaped symbol plus a word, no boxed chip. Shape carries the state as well as hue.
  function StatusBadge(p) {
    var s = p.status || 'draft';
    return h('span', { className: 'br-status', 'data-status': s }, h('i', { className: 'br-mark', 'data-status': s, 'aria-hidden': true }), h('span', null, p.children || STATUS_WORDS[s] || s));
  }
  // PhaseTimeline: rows on a week axis; selecting a row highlights it and opens its panel underneath. One open at a time.
  function PhaseTimeline(p) {
    var phases = p.phases || [], total = p.weeks || phases.reduce(function (m, x) { return Math.max(m, x.end); }, 0) || 1;
    var cur = useState(p.defaultSelected == null ? (p.defaultOpen == null ? 0 : p.defaultOpen) : p.defaultSelected);
    var open = useState(p.defaultOpen === undefined ? 0 : p.defaultOpen);
    var uid = useState(function () { return 'br-tl-' + Math.random().toString(36).slice(2, 8); })[0];
    function pick(i) { var shut = cur[0] === i && open[0] === i; cur[1](i); open[1](shut ? null : i); if (p.onSelect) p.onSelect(phases[i], i); }
    var unit = p.unit || 'wk';
    return h('div', { className: 'br-tl br-tl-x-on' }, phases.map(function (ph, i) {
      var on = cur[0] === i, isOpen = open[0] === i, pid = uid + '-' + i, max = Math.max(ph.planned || 0, ph.actual || 0) || 1, u = ph.unit || unit;
      var row = h('div', { key: 'r' + i, className: 'br-tl-row', role: 'button', tabIndex: 0, 'aria-current': on ? 'true' : 'false', 'aria-expanded': isOpen, 'aria-controls': pid,
          onClick: function () { pick(i); }, onKeyDown: function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(i); } } },
        h('span', { className: 'br-counter' }, i + 1), h('span', { className: 'br-tl-name' }, ph.name),
        h('div', { className: 'br-tl-track' }, h('div', { className: 'br-tl-bar', style: { left: (ph.start / total * 100) + '%', width: ((ph.end - ph.start) / total * 100) + '%' } })));
      var chart = (ph.planned != null || ph.actual != null) ? h('div', { className: 'br-tl-ch' }, h('span', { className: 'br-label' }, ph.chartLabel || p.chartLabel || 'Weeks, planned and actual'),
        [['Planned', ph.planned, 'p'], ['Actual', ph.actual, 'a']].map(function (b) {
          return b[1] == null ? null : h('div', { key: b[2] }, h('span', { className: 'br-label' }, b[0]), h('span', { className: 'br-tl-cb' }, h('i', { className: b[2], style: { '--r': b[1] / max } }), h('b', null, b[1] + ' ' + u)));
        })) : null;
      var ms = ph.milestones && ph.milestones.length ? h('div', { className: 'br-tl-mw' }, h('span', { className: 'br-label' }, p.milestonesLabel || 'Milestones'),
        h('ul', { className: 'br-tl-ms' }, ph.milestones.map(function (m, k) {
          return h('li', { key: k, className: m.done ? 'is-done' : undefined }, h('i', { 'aria-hidden': true }), h('span', null, m.label), h('small', null, m.done ? (p.doneLabel || 'Done') : (p.openLabel || 'Open')));
        }))) : null;
      var panel = h('div', { key: 'x' + i, id: pid, className: cx('br-tl-x', isOpen && 'is-open'), role: 'region', 'aria-label': ph.name + ' detail' },
        h('div', null, h('div', { className: 'br-tl-xin' }, chart, ms, ph.detail ? h('div', { className: 'br-tl-note' }, ph.detail) : null)));
      return [row, panel];
    }));
  }
  // CellReveal: case-study cells; each takes a soft signal tint, coral, blue, green, orange in order unless tint is set.
  var TINTS = ['violet', 'indigo', 'blue', 'teal'];
  function CellReveal(p) {
    return h('div', { className: 'br-reveal-row' }, (p.cells || []).map(function (c, i) {
      return h('a', { key: i, className: 'br-reveal', href: c.href || '#', 'data-tint': c.tint || TINTS[i % 4] },
        c.image ? h('img', { className: 'br-reveal-img', src: c.image, alt: c.alt || '' }) : h('span', { className: 'br-reveal-photo' }, c.placeholder || 'Photograph'),
        h('span', { className: 'br-reveal-panel' }),
        h('span', { className: 'br-reveal-pin' }, h('span', null, h('span', { className: 'br-label' }, c.label), h('span', { className: 'br-reveal-title' }, c.title)), c.number != null ? h('span', { className: 'br-reveal-num' }, c.number) : null));
    }));
  }
  // Divider: hairline or labelled (label in the line). strong and dots stay for older pages.
  function Divider(p) {
    var v = p.variant || 'hairline';
    if (v === 'labelled') return h('div', { className: 'br-dv br-dv-label', role: 'separator', 'aria-label': p.label }, h('span', null, p.label));
    if (v === 'strong') return h('div', { className: 'br-dv br-dv-strong', role: 'separator' });
    if (v === 'dots') return h('div', { className: 'br-dv br-dv-dots', role: 'separator' }, h('i'), h('i'), h('i'));
    return h('div', { className: 'br-dv', role: 'separator' });
  }
  // TierPicker: one tier, then add-ons, with a running total. The selected tier takes the action fill.
  function TierPicker(p) {
    var tiers = p.tiers || [], addons = p.addons || [];
    var sel = useState(p.defaultTier == null ? null : p.defaultTier), on = useState(p.defaultAddons || []);
    var refs = [];
    function fmt(v) { return (p.prefix || '') + v + (p.suffix || ''); }
    function key(e, i) { var n = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0; if (!n) return; e.preventDefault(); var j = (i + n + tiers.length) % tiers.length; sel[1](j); if (refs[j]) refs[j].focus(); }
    var total = (sel[0] == null ? 0 : (tiers[sel[0]].price || 0)) + on[0].reduce(function (s, k) { return s + (addons[k].price || 0); }, 0);
    return h('div', { className: 'br-tier' },
      h('div', { className: 'br-tier-g', role: 'radiogroup', 'aria-label': p.label || 'Tier' }, tiers.map(function (t, i) {
        var chk = sel[0] === i;
        return h('button', { key: i, ref: function (el) { refs[i] = el; }, type: 'button', role: 'radio', 'aria-checked': chk, tabIndex: chk || (sel[0] == null && i === 0) ? 0 : -1, onClick: function () { sel[1](i); }, onKeyDown: function (e) { key(e, i); } },
          h('small', null, t.label), h('strong', null, t.name), h('em', null, fmt(t.price)), t.priceNote ? h('small', { className: 'br-tier-pn' }, t.priceNote) : null,
          (t.scope || []).map(function (l, k) { return h('span', { key: k }, l); }));
      })),
      addons.length ? h('fieldset', { className: 'br-tier-a' }, h('legend', { className: 'br-label' }, p.addonsLabel || 'Add-ons'), addons.map(function (a, k) {
        var c = on[0].indexOf(k) > -1;
        return h('label', { key: k }, h('input', { type: 'checkbox', checked: c, onChange: function () { on[1](c ? on[0].filter(function (x) { return x !== k; }) : on[0].concat([k])); } }), h('i', { 'aria-hidden': true }), h('span', null, a.name), h('em', null, '+' + fmt(a.price)));
      })) : null,
      p.totalLabel === false ? null : h('div', { className: 'br-tier-t', 'aria-live': 'polite' }, h('span', { className: 'br-label' }, p.totalLabel || 'Total'), h('b', null, fmt(total))));
  }
  // AvatarStack: overlapping avatars; the surface ring and line-strong edge keep each one apart.
  function AvatarStack(p) {
    var max = p.max || 4, names = p.names || [], shown = names.slice(0, max), more = names.length - shown.length;
    return h('span', { className: cx('br-avstack', p.size === 'sm' && 'is-sm'), role: 'group', 'aria-label': p.label || names.join(', ') },
      shown.map(function (n) { return h(Avatar, { key: n, name: n, size: p.size }); }),
      more > 0 ? h('span', { className: cx('mer-avatar', 'br-avmore', p.size === 'sm' && 'mer-avatar-sm'), 'aria-hidden': true }, '+' + more) : null);
  }
  window.Meridian = { Icon: Icon, Logo: Logo, Button: Button, IconButton: IconButton, Tag: Tag, StateText: StateText, Avatar: Avatar, Field: Field, Search: Search, Checkbox: Checkbox, Toggle: Toggle, Tabs: Tabs, Segmented: Segmented, Breadcrumb: Breadcrumb, Pagination: Pagination, Card: Card, Metric: Metric, FactBand: FactBand, DataTable: DataTable, RecordRow: RecordRow, DetailPanel: DetailPanel, Timeline: Timeline, DecisionList: DecisionList, WeekStrip: WeekStrip, DealBoard: DealBoard, StageSpine: StageSpine, ColumnChart: ColumnChart, EmptyState: EmptyState, Sidebar: Sidebar, TopBar: TopBar, Conversation: Conversation, Dialog: Dialog, Toast: Toast, Tooltip: Tooltip, Menu: Menu, FilterBar: FilterBar, Skeleton: Skeleton, Progress: Progress, Callout: Callout, ProposedChange: ProposedChange, Grounds: Grounds, Quote: Quote, AgentActivity: AgentActivity, SectionChanges: SectionChanges, StatusBadge: StatusBadge, PhaseTimeline: PhaseTimeline, CellReveal: CellReveal, Divider: Divider, TierPicker: TierPicker, AvatarStack: AvatarStack };
  window.LLC = Object.assign(window.Meridian, window.LLCMarks || {});
})();
;(function(){var n=window.LLC;if(n&&window.LLCInteractions)n.interactions=window.LLCInteractions})();
// Gradient icons: one shared gradient definition that any icon stroke can point at (url(#llc-ig)). Its stops read --llc-ig-1 to -3, so they follow the theme.
;(function(){function add(){if(document.getElementById('llc-icon-defs'))return;var d=document.createElement('div');d.innerHTML='<svg id="llc-icon-defs" width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false"><defs><linearGradient id="llc-ig" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse"><stop offset="0" style="stop-color:var(--llc-ig-1,#7b5cd6)"></stop><stop offset=".5" style="stop-color:var(--llc-ig-2,#3b3f9c)"></stop><stop offset="1" style="stop-color:var(--llc-ig-3,#2f6fde)"></stop></linearGradient></defs></svg>';document.body.appendChild(d.firstChild)}if(document.body)add();else document.addEventListener('DOMContentLoaded',add)})();

/* LiveLaughCode page components (19 Nov): FAQ, table of contents, contact form, code block, mobile menu. */
(function(){
function init(root){root=root||document;
 root.querySelectorAll('[data-llc-faq]').forEach(function(f){if(f.__llc)return;f.__llc=1;var a=f.querySelector('.a');f.querySelectorAll('button[role="tab"]').forEach(function(b){b.addEventListener('click',function(){f.querySelectorAll('button[role="tab"]').forEach(function(x){x.setAttribute('aria-selected',String(x===b))});a.querySelector('h3').textContent=b.textContent;a.querySelector('p').textContent=b.getAttribute('data-answer')||''})})});
 root.querySelectorAll('[data-llc-toc]').forEach(function(t){if(t.__llc)return;t.__llc=1;var ls=[].slice.call(t.querySelectorAll('a')),fill=t.querySelector('.fill');
  function set(l){ls.forEach(function(x){x.classList.toggle('on',x===l)});if(fill&&l)fill.style.height=(l.offsetTop-30+l.offsetHeight)+'px'}
  ls.forEach(function(l){l.addEventListener('click',function(){set(l)})});
  var targets=ls.map(function(l){var h=l.getAttribute('href');return h&&h.charAt(0)==='#'?document.getElementById(h.slice(1)):null});
  if(window.IntersectionObserver&&targets.some(Boolean)){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var i=targets.indexOf(e.target);if(i>-1)set(ls[i])}})},{rootMargin:'0px 0px -70% 0px'});targets.forEach(function(x){if(x)io.observe(x)})}
  set(t.querySelector('a.on')||ls[0])});
 root.querySelectorAll('[data-llc-contact]').forEach(function(c){if(c.__llc)return;c.__llc=1;
  c.querySelectorAll('.llc-needs,.llc-slots').forEach(function(g){g.querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){g.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',String(x===b))})})})})});
 root.querySelectorAll('.llc-codeblock button').forEach(function(b){if(b.__llc)return;b.__llc=1;b.addEventListener('click',function(){var t=b.parentNode.textContent.replace(b.textContent,'').trim();if(navigator.clipboard)navigator.clipboard.writeText(t).catch(function(){});b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1200)})});
 root.querySelectorAll('.llc-burger').forEach(function(b){if(b.__llc)return;b.__llc=1;var m=document.getElementById(b.getAttribute('aria-controls'));b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(o));b.textContent=o?'×':'☰';if(m)m.classList.toggle('is-open',o)})});
}
window.LLCPage={init:init};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){init()});else init();
})();

/* DataTable wiring (19 Nov). Call LLCPage.init(root) after adding a table. */
(function(){
var prev=window.LLCPage&&window.LLCPage.init;
function cellVal(td){var v=td.getAttribute('data-sort');if(v==null)v=td.textContent.trim();var t=String(v).trim();if(/^-?\$?[\d.,]+[KkM%]?$/.test(t)){var n=parseFloat(t.replace(/[$,]/g,''));if(/M$/.test(t))n*=1000;return n}return t.toLowerCase()}
function tables(root){
 root.querySelectorAll('table[data-llc-sort]').forEach(function(t){if(t.__llcs)return;t.__llcs=1;var tb=t.tBodies[0],ths=[].slice.call(t.tHead.rows[0].cells);
  ths.forEach(function(th,ci){var b=th.querySelector('button');if(!b)return;b.addEventListener('click',function(){var cur=th.getAttribute('aria-sort');var dir=cur==='ascending'?'descending':cur==='descending'?'ascending':(th.classList.contains('n')?'descending':'ascending');
   ths.forEach(function(x){x.removeAttribute('aria-sort')});th.setAttribute('aria-sort',dir);var m=dir==='ascending'?1:-1;
   var rows=[].slice.call(tb.rows).filter(function(r){return !r.classList.contains('more')});
   rows.sort(function(a,b){var x=cellVal(a.cells[ci]),y=cellVal(b.cells[ci]);return (x>y?1:x<y?-1:0)*m});
   rows.forEach(function(r){var nx=r.nextElementSibling&&r.nextElementSibling.classList.contains('more')?r.nextElementSibling:null;tb.appendChild(r);if(nx)tb.appendChild(nx)})})})});
 root.querySelectorAll('table.llc-tbl.open tr.row').forEach(function(r){if(r.__llc)return;r.__llc=1;if(!r.hasAttribute('tabindex'))r.tabIndex=0;if(!r.hasAttribute('aria-expanded'))r.setAttribute('aria-expanded','false');
  function tg(e){if(e.target.closest('label,input,button,a'))return;r.setAttribute('aria-expanded',String(r.getAttribute('aria-expanded')!=='true'))}
  r.addEventListener('click',tg);r.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();tg(e)}})});
 root.querySelectorAll('[data-llc-select]').forEach(function(w){if(w.__llc)return;w.__llc=1;var all=w.querySelector('thead input'),boxes=w.querySelectorAll('tbody input[type=checkbox]'),bar=w.querySelector('.llc-tbar');
  function up(){var n=0;boxes.forEach(function(b){b.closest('tr').classList.toggle('is-selected',b.checked);if(b.checked)n++});if(bar){bar.hidden=!n;var s=bar.querySelector('span');if(s)s.textContent=n+' selected'}if(all){all.checked=n===boxes.length;all.indeterminate=n>0&&n<boxes.length}}
  boxes.forEach(function(b){b.addEventListener('change',up)});if(all)all.addEventListener('change',function(){boxes.forEach(function(b){b.checked=all.checked});up()});
  var c=w.querySelector('[data-llc-clear]');if(c)c.addEventListener('click',function(){boxes.forEach(function(b){b.checked=false});up()});up()});
 root.querySelectorAll('table[data-llc-colhl]').forEach(function(t){if(t.__llc)return;t.__llc=1;function hl(i){t.querySelectorAll('tr').forEach(function(r){[].forEach.call(r.cells,function(c,j){c.classList.toggle('hl',j===i&&i>0)})})}
  t.addEventListener('mouseover',function(e){var c=e.target.closest('td,th');if(c)hl(c.cellIndex)});t.addEventListener('mouseleave',function(){hl(-1)})});
 root.querySelectorAll('.llc-tsplit').forEach(function(w){if(w.__llc)return;w.__llc=1;var bs=w.querySelectorAll('.list button'),ps=w.querySelectorAll('[data-panel]');
  function show(i){bs.forEach(function(b,j){b.setAttribute('aria-pressed',String(j===i))});ps.forEach(function(p,j){p.classList.toggle('on',j===i)})}
  bs.forEach(function(b,i){b.addEventListener('click',function(){show(i)})});var s=0;bs.forEach(function(b,i){if(b.getAttribute('aria-pressed')==='true')s=i});show(s)});
}
function init(root){root=root||document;if(prev)prev(root);tables(root)}
window.LLCPage={init:init};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){tables(document)});else tables(document);
})();
