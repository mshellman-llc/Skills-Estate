"""Execute the guide's inline JavaScript with a bounded DOM double, without a browser.

These checks cover event wiring and state changes. They do not check browser
parsing, layout, accessibility behavior or rendered output.
"""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/assess-solution-delivery/assets/field-guide.body.html'


class FixtureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = {'tag': 'document', 'attrs': {}, 'children': [], 'text': ''}
        self.stack = [self.root]
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': [], 'text': ''}
        self.stack[-1]['children'].append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack[-1]['tag'] == tag:
            node = self.stack.pop()
            if tag == 'script':
                if 'src' in node['attrs']:
                    raise ValueError('The test does not fetch external scripts')
                self.scripts.append(node['text'])

    def handle_data(self, data):
        self.stack[-1]['text'] += data


HARNESS = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert/strict');
const fixture = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
class Element {
  constructor(node) {
    this.tag = node.tag; this.attrs = {...node.attrs}; this.listeners = {};
    this.children = []; this._text = node.text || ''; this._html = '';
    this.value = this.attrs.value || '';
    this.classList = {
      contains: c => this.classes().includes(c),
      add: c => { this.className = [...new Set([...this.classes(), c])].join(' '); },
      remove: c => { this.className = this.classes().filter(x => x !== c).join(' '); },
      toggle: (c, enabled) => { const use = enabled === undefined ? !this.classList.contains(c) : enabled;
                              this.classList[use ? 'add' : 'remove'](c); return use; }
    };
    (node.children || []).forEach(child => this.appendChild(new Element(child)));
  }
  classes() { return (this.attrs.class || '').split(/\s+/).filter(Boolean); }
  get className() { return this.attrs.class || ''; }
  set className(value) { this.attrs.class = value; }
  get textContent() { return this._text + this.children.map(x => x.textContent).join(''); }
  set textContent(value) { this._text = String(value); this.children = []; }
  get innerHTML() { return this._html; }
  set innerHTML(value) { this._html = String(value); this.children = []; }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  getAttribute(name) { return this.attrs[name] ?? null; }
  appendChild(child) { child.parent = this; this.children.push(child); return child; }
  matches(selector) {
    if (/^\.[\w-]+$/.test(selector)) return this.classList.contains(selector.slice(1));
    if (/^#[\w-]+$/.test(selector)) return this.attrs.id === selector.slice(1);
    const attr = selector.match(/^([\w-]+)\[([\w-]+)\]$/);
    if (attr) return this.tag === attr[1] && Object.hasOwn(this.attrs, attr[2]);
    throw Error('Unsupported DOM selector: ' + selector);
  }
  querySelectorAll(selector) {
    const found = [];
    for (const child of this.children) {
      if (child.matches(selector)) found.push(child);
      found.push(...child.querySelectorAll(selector));
    }
    return found;
  }
  closest(selector) { return this.matches(selector) ? this : (this.parent?.closest(selector) || null); }
  addEventListener(type, callback) { (this.listeners[type] ||= []).push(callback); }
  dispatch(type, target = this) {
    for (const callback of this.listeners[type] || []) callback.call(this, {target});
  }
}
const document = new Element(fixture.root);
document.getElementById = id => document.querySelectorAll('#' + id)[0] || null;
document.createElement = tag => new Element({tag, attrs: {}, children: []});
const context = vm.createContext({document});
for (const script of fixture.scripts) vm.runInContext(script, context, {timeout: 1000});
const get = id => { const node = document.getElementById(id); assert.ok(node, id); return node; };
const click = (parent, child) => get(parent).dispatch('click', child);
const activeCount = (parent, selector) => get(parent).querySelectorAll(selector).filter(x => x.classList.contains('active')).length;
const group = process.argv[3];
let assertions = 0;
function equal(actual, expected) { assert.deepEqual(actual, expected); assertions++; }
if (group === 'calculator') {
  equal(get('prRate').textContent, '$12');
  equal(get('prCost').textContent, '$24 – $48');
  equal(get('prCompare').textContent, 'At extended review rates: $36 – $72');
  const roles = get('prRoles').querySelectorAll('.pr-rb');
  equal(roles.map(r => r.textContent), ['Sample intake', 'Technical review', 'Export check']);
  const tiers = get('prToggle').querySelectorAll('.pr-tb');
  const expected = [[12, 18], [24, 36], [8, 12]];
  for (let r=0; r<roles.length; r++) for (let t=0; t<tiers.length; t++) {
    click('prRoles', roles[r]); click('prToggle', tiers[t]);
    equal(get('prRate').textContent, '$' + expected[r][t]);
    equal(get('prCost').textContent, '$' + 2*expected[r][t] + ' – $' + 4*expected[r][t]);
    equal(get('prRoleName').textContent, roles[r].textContent);
    equal(get('prStatusName').textContent, t ? 'extended review' : 'standard review');
    equal(activeCount('prRoles', '.pr-rb'), 1); equal(activeCount('prToggle', '.pr-tb'), 1);
  }
} else if (group === 'ranges') {
  for (const [low, high] of [['-1','2'], ['5','2'], ['Infinity','9'], ['0','NaN']]) {
    get('prLow').value=low; get('prHigh').value=high; get('prLow').dispatch('input');
    equal(get('prLow').getAttribute('aria-invalid'), 'true');
    equal(get('prHigh').getAttribute('aria-invalid'), 'true');
    equal(get('prCost').textContent, 'Enter nonnegative days with maximum ≥ minimum');
    equal(get('prCompare').textContent, '');
  }
  for (const [low, high, cost] of [['0','0','$0 – $0'], ['1.5','2.5','$18 – $30'], ['3','3','$36 – $36']]) {
    get('prLow').value=low; get('prHigh').value=high; get('prHigh').dispatch('input');
    equal(get('prLow').getAttribute('aria-invalid'), 'false');
    equal(get('prHigh').getAttribute('aria-invalid'), 'false');
    equal(get('prCost').textContent, cost);
  }
} else if (group === 'flow') {
  const chips = get('iflSteps').querySelectorAll('.ifl-chip');
  const titles = ['Submit a sample','Validate metadata','Assign the reviewer','Record the decision',
                  'Resolve an exception','Confirm export access','Export the result'];
  equal(chips.length, 7);
  for (let i=0; i<7; i++) {
    const child = document.createElement('span'); chips[i].appendChild(child);
    click('iflSteps', child);
    assert.ok(get('iflDetail').innerHTML.includes((i+1)+'. '+titles[i])); assertions++;
    assert.ok(get('iflDetail').innerHTML.includes('Synthetic test specification, case '+(i+1))); assertions++;
    equal(activeCount('iflSteps', '.ifl-chip'), 1);
    equal(chips[i].classList.contains('active'), true);
  }
} else if (group === 'ledger') {
  const rows = document.querySelectorAll('tr[data-disp]'); equal(rows.length, 12);
  for (const pill of get('ldfPills').querySelectorAll('.ldf-p')) {
    click('ldfPills', pill);
    const filter = pill.getAttribute('data-f');
    const visible = rows.filter(r => !r.classList.contains('hide-row'));
    equal(visible.length, {all:12,native:4,config:4,custom:3,dep:1}[filter]);
    if (filter !== 'all') equal(visible.every(r => r.getAttribute('data-disp')===filter), true);
    equal(activeCount('ldfPills','.ldf-p'), 1);
  }
  click('ldfPills', get('ldfPills').querySelectorAll('.ldf-p')[0]);
  equal(rows.filter(r => !r.classList.contains('hide-row')).length, 12);
} else if (group === 'views') {
  const views = document.querySelectorAll('.ct-view');
  equal(views.filter(v => v.classList.contains('show')).map(v => v.getAttribute('data-view')), ['current']);
  for (const value of ['target','current']) {
    const button = get('ctToggle').querySelectorAll('.ct-tb').find(b => b.getAttribute('data-view')===value);
    click('ctToggle', button);
    equal(views.filter(v => v.classList.contains('show')).map(v => v.getAttribute('data-view')), [value]);
    equal(activeCount('ctToggle','.ct-tb'), 1);
  }
} else { throw Error('Unknown group'); }
console.log(JSON.stringify({group, assertions, scope:'inline JavaScript event/state checks; no browser rendering'}));
'''


class FieldGuideInteractionTests(unittest.TestCase):
    def run_group(self, group):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for inline interaction logic tests')
        parser = FixtureParser()
        parser.feed(SOURCE.read_text())
        self.assertTrue(parser.scripts)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            script = directory / 'harness.cjs'
            script.write_text(HARNESS)
            fixture = directory / 'fixture.json'
            fixture.write_text(json.dumps({'root': parser.root, 'scripts': parser.scripts}))
            result = subprocess.run([node, str(script), str(fixture), group],
                                    capture_output=True, text=True, timeout=10)
            (directory / 'result.json').write_text(json.dumps({'exit': result.returncode,
                'stdout': result.stdout, 'stderr': result.stderr}, indent=2))
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertGreater(report['assertions'], 0)
            print(json.dumps(report))

    def test_calculator_roles_and_tiers(self):
        self.run_group('calculator')

    def test_range_errors_and_recovery(self):
        self.run_group('ranges')

    def test_seven_flow_steps_and_delegated_clicks(self):
        self.run_group('flow')

    def test_ledger_filters_and_restore_all(self):
        self.run_group('ledger')

    def test_current_target_toggle(self):
        self.run_group('views')

    def test_ledger_bar_matches_actual_row_counts(self):
        source = SOURCE.read_text()
        counts = Counter(re.findall(r'<tr data-disp="([a-z]+)"', source))
        self.assertEqual({'native': 4, 'config': 4, 'custom': 3, 'dep': 1}, dict(counts))
        widths = dict(re.findall(r'class="ldf-seg ([a-z]+)" style="width:([0-9.]+)%"', source))
        self.assertEqual(set(counts), set(widths))
        for kind, count in counts.items():
            self.assertAlmostEqual(float(widths[kind]), 100 * count / sum(counts.values()), places=5)
        self.assertAlmostEqual(sum(map(float, widths.values())), 100, places=5)


if __name__ == '__main__':
    unittest.main()
