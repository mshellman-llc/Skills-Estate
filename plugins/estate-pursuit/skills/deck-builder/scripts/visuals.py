"""Render semantic diagrams as local, selectable SVG and accessible HTML."""
import html
import math
import re
import textwrap


def text(value, name='text'):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must contain text')
    return html.escape(value, quote=True)


def number(value, name, low=0, high=10000):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(name + ' is outside the permitted range')
    return value


def identity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', value):
        raise ValueError('Use an identifier beginning with a letter')
    return value


def rows(items, name):
    if not isinstance(items, list) or not items:
        raise ValueError(name + ' must be a nonempty list')
    return items


def svg_text(value, x, y, width, cls='diagram-label', anchor='middle', max_lines=3):
    text(value)
    lines = textwrap.wrap(value, max(8, int(width / 13)), break_long_words=False, break_on_hyphens=False)
    if len(lines) > max_lines:
        raise ValueError('Diagram label needs more space: ' + value)
    first = y - (len(lines)-1)*14
    return f'<text class="{cls}" x="{x}" y="{first}" text-anchor="{anchor}">' + ''.join(f'<tspan x="{x}" dy="{0 if i==0 else 28}">{text(line)}</tspan>' for i,line in enumerate(lines)) + '</text>'


def frame(body, description, prefix, height, reading, caption):
    title_id = prefix + '-description'
    return (f'<figure class="visual"><div class="visual-scroll" tabindex="0" role="region" aria-label="Diagram; scroll horizontally on a narrow screen">'
            f'<svg viewBox="0 0 1120 {height}" role="img" aria-labelledby="{title_id}" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="{title_id}">{text(description)}</title><defs><marker id="{prefix}-arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M 1 1 L 8 5 L 1 9" class="arrow-head"/></marker></defs>'
            + body + '</svg></div><p class="scroll-hint">Scroll diagram horizontally.</p>' + ('<figcaption>'+text(caption)+'</figcaption>' if caption else '')
            + '<ol class="visual-reading">' + ''.join('<li>'+r+'</li>' for r in reading) + '</ol></figure>')


def sequence(block, prefix):
    actors = rows(block.get('actors'), 'actors')
    if not 2 <= len(actors) <= 4:
        raise ValueError('A sequence supports two to four actors; split larger interactions')
    positions = {}; body = ''; reading = []
    for i, actor in enumerate(actors):
        key = identity(actor.get('id'))
        if key in positions: raise ValueError('Duplicate actor: '+key)
        width=min(320,1000/len(actors)-16)
        x = width/2+10 + i*(1100-width)/(len(actors)-1); positions[key] = x
        body += f'<rect x="{x-width/2}" y="8" width="{width}" height="48" class="actor"/>'
        body += svg_text(actor.get('label'), x, 39, width-10, max_lines=1)
    events = rows(block.get('events'), 'events')
    height = 100 + 64*len(events)
    if height > 490: raise ValueError('Split the sequence after six events')
    for key,x in positions.items():
        body += f'<path d="M{x} 56 V{height-10}" class="lifeline"/>'
    for i,event in enumerate(events):
        start = event.get('from'); end = event.get('to'); label = event.get('label')
        if start not in positions or end not in positions: raise ValueError('Unknown sequence actor')
        if start == end: raise ValueError('Use a separate note for an actor state')
        x1,x2 = positions[start],positions[end]; y=106+i*64
        lost = event.get('lost',False)
        if not isinstance(lost,bool):raise ValueError('lost must be boolean')
        line_class = 'message lost' if lost else 'message'
        body += f'<g data-from="{identity(start)}" data-to="{identity(end)}" data-lost="{str(lost).lower()}">'
        body += f'<path d="M{x1} {y} H{x2}" class="{line_class}"' + ('' if lost else f' marker-end="url(#{prefix}-arrow)"') + '/>'
        if lost: body += f'<path d="M{x2-7} {y-7} l14 14 M{x2-7} {y+7} l14 -14" class="message"/>'
        body += svg_text(label,(x1+x2)/2,y-14,abs(x2-x1)-30,max_lines=1)+'</g>'
        names={a['id']:a['label'] for a in actors}
        reading.append(text(names[start])+' → '+text(names[end])+': '+text(label)+(' (response lost)' if lost else ''))
    return frame(body,block.get('description'),prefix,height,reading,block.get('caption',block.get('description')))


def diagram(block, prefix):
    height=number(block.get('height',400),'height',180,490)
    nodes={};body='';reading=[]
    for zone in block.get('zones',[]):
        x=number(zone.get('x'),'zone x',0,1120);y=number(zone.get('y'),'zone y',0,height)
        w=number(zone.get('w'),'zone width',40,1120);h=number(zone.get('h'),'zone height',40,height)
        if x+w>1120 or y+h>height:raise ValueError('Zone exceeds diagram bounds')
        body+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="zone"/>'
        body+=svg_text(zone.get('label'),x+16,y+30,w-32,cls='zone-label',anchor='start',max_lines=1)
        reading.append('Region: '+text(zone['label']))
    for node in rows(block.get('nodes'),'nodes'):
        key=identity(node.get('id'))
        if key in nodes:raise ValueError('Duplicate diagram node: '+key)
        x=number(node.get('x'),'node x',0,1120);y=number(node.get('y'),'node y',0,height)
        w=number(node.get('w',210),'node width',70,1120);h=number(node.get('h',76),'node height',50,height)
        if x+w>1120 or y+h>height:raise ValueError('Node exceeds diagram bounds')
        kind=node.get('kind','process')
        if kind not in ('process','decision','external','note','emphasis'):raise ValueError('Unknown node kind')
        nodes[key]={**node,'x':x,'y':y,'w':w,'h':h,'kind':kind}
        text(node.get('label'))
    edge_parts=[]
    for edge in rows(block.get('edges'),'edges'):
        a,b=edge.get('from'),edge.get('to')
        if a not in nodes or b not in nodes:raise ValueError('Unknown diagram endpoint')
        def port(key,side):
            n=nodes[key];x,y,w,h=n['x'],n['y'],n['w'],n['h']
            ports={'left':(x,y+h/2),'right':(x+w,y+h/2),'top':(x+w/2,y),'bottom':(x+w/2,y+h)}
            if side not in ports:raise ValueError('Unknown node port')
            return ports[side]
        points=[port(a,edge.get('from_side','right'))]
        for p in edge.get('via',[]):
            if not isinstance(p,list) or len(p)!=2:raise ValueError('Each bend needs x and y')
            points.append((number(p[0],'bend x',0,1120),number(p[1],'bend y',0,height)))
        points.append(port(b,edge.get('to_side','left')))
        style=edge.get('style','solid')
        if style not in ('solid','dashed'):raise ValueError('Unknown edge style')
        path='M'+' L'.join(f'{x} {y}' for x,y in points)
        edge_parts.append(f'<path data-from="{identity(a)}" data-to="{identity(b)}" d="{path}" class="edge {style}" marker-end="url(#{prefix}-arrow)"/>')
        label=edge.get('label');text(label)
        lx=number(edge.get('label_x',(points[0][0]+points[-1][0])/2),'label x',0,1120)
        ly=number(edge.get('label_y',(points[0][1]+points[-1][1])/2-15),'label y',0,height)
        lw=number(edge.get('label_width',240),'label width',70,700)
        # A halo keeps labels readable when an edge passes behind them.
        edge_parts.append(svg_text(label,lx,ly,lw,cls='edge-label',max_lines=2))
        reading.append(text(nodes[a]['label'])+' → '+text(nodes[b]['label'])+': '+text(label))
    body+=''.join(edge_parts)
    for key,n in nodes.items():
        x,y,w,h=n['x'],n['y'],n['w'],n['h']
        if n['kind']=='decision':
            body+=f'<polygon data-node="{key}" points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" class="node decision"/>'
        else:
            body+=f'<rect data-node="{key}" x="{x}" y="{y}" width="{w}" height="{h}" class="node {n["kind"]}"/>'
        body+=svg_text(n['label'],x+w/2,y+h/2+7,w*(.65 if n['kind']=='decision' else .94),max_lines=max(1,int(h/28)))
        # The relationship list already names every connected node.
    return frame(body,block.get('description'),prefix,height,reading,block.get('caption',block.get('description')))


def specimen(block, prefix):
    fields=rows(block.get('fields'),'fields')
    caption=block.get('caption',block.get('description'))
    markup='<figure class="specimen">'+('<figcaption>'+text(caption)+'</figcaption>' if caption else '')+'<div class="record"><h3>'+text(block.get('title'))+'</h3><dl>'
    for field in fields:
        markup+='<div class="record-row"><dt>'+text(field.get('label'))+'</dt><dd>'+text(field.get('value'))+'</dd><dd class="annotation">'+text(field.get('why'))+'</dd></div>'
    return markup+'</dl></div></figure>'


def bars(block, prefix):
    items=rows(block.get('items'),'bar items')
    if len(items)>6:raise ValueError('Split bar comparisons with more than six categories')
    maximum=number(block.get('maximum'),'scale maximum',.000001)
    unit=text(block.get('unit'));reading=[];body=''
    for i,item in enumerate(items):
        value=number(item.get('value'),'bar value',0,maximum); label=item.get('label');text(label)
        y=30+i*57
        body+=svg_text(label,250,y+22,240,anchor='end',max_lines=1)
        body+=f'<rect x="280" y="{y}" width="{660*value/maximum}" height="30" class="bar"/>'
        body+=svg_text(f'{value:g} '+block['unit'],960,y+23,150,anchor='start',max_lines=1)
        reading.append(text(label)+': '+text(f'{value:g} '+block['unit']))
    h=85+57*len(items)
    body+=f'<path d="M280 15 V{h-40} H940" class="axis"/>'
    body+=svg_text('0',280,h-12,90,max_lines=1)+svg_text(f'{maximum:g} '+block['unit'],940,h-12,210,max_lines=1)
    return frame(body,block.get('description'),prefix,h,reading,block.get('caption',block.get('description')))


def render_visual(block,prefix):
    if 'caption' in block and not isinstance(block['caption'],str):raise ValueError('caption must be text')
    builders={'sequence':sequence,'diagram':diagram,'specimen':specimen,'bars':bars}
    return builders[block['type']](block,prefix)
