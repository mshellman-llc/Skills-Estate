"""Behavior tests of the isolated deck package's visual input contract."""
import copy
import json
import sys
import unittest
from pathlib import Path
from test_deck_html import DeckTests, Markup

class VisualTests(DeckTests):
    def setUp(self):
        super().setUp()
        self.data=json.loads((self.pkg/'examples/reconciliation-narrative.json').read_text())

    def test_isolated_package_preserves_content_and_sources(self):
        result,dest=self.run_build();self.assertEqual(result.returncode,0,result.stderr)
        doc=Markup();doc.feed(dest.read_text());tags=doc.tags
        self.assertEqual(sum(tag=='section' for tag,attrs in tags),15)
        for slide in self.data['slides']:
            self.assertIn(slide['title'],doc.text)
            for block in slide['blocks']:
                for edge in block.get('edges',[]):
                    self.assertTrue(any(a.get('data-from')==edge['from'] and a.get('data-to')==edge['to'] for t,a in tags))
        for source in self.data['sources'].values():self.assertIn(source,doc.text)
        ids=[a['id'] for t,a in tags if 'id' in a];self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(any(a.get('data-lost')=='true' and a.get('data-from')=='ledger' for t,a in tags))
        self.assertFalse(any(t=='script' for t,a in tags))

    def test_optional_copy_preserves_accessible_description(self):
        data=copy.deepcopy(self.data);data['slides']=data['slides'][:1]
        data['slides'][0].pop('lead',None);data['slides'][0]['blocks'][0]['caption']=''
        result,dest=self.run_build(data);self.assertEqual(result.returncode,0,result.stderr)
        doc=Markup();doc.feed(dest.read_text());self.assertFalse(any(t=='figcaption' for t,a in doc.tags))
        self.assertIn(data['slides'][0]['blocks'][0]['description'],doc.text)
        data['slides'][0]['blocks'][0]['caption']=False
        result,dest=self.run_build(data,output='bad-caption.html');self.assertEqual(result.returncode,2);self.assertFalse(dest.exists())

    def test_invalid_connections_bounds_and_numbers_refuse_output(self):
        for index,mutation in enumerate(('endpoint','duplicate','bounds','nan','sequence')):
            data=copy.deepcopy(self.data);graph=data['slides'][0]['blocks'][0]
            if mutation=='endpoint':graph['edges'][0]['to']='missing'
            elif mutation=='duplicate':graph['nodes'][1]['id']=graph['nodes'][0]['id']
            elif mutation=='bounds':graph['nodes'][0]['x']=1110
            elif mutation=='nan':graph['nodes'][0]['x']=float('nan')
            else:data['slides'][1]['blocks'][0]['events'][0]['to']='missing'
            result,dest=self.run_build(data,output=f'invalid-{index}.html')
            self.assertEqual(result.returncode,2,result.stderr);self.assertFalse(dest.exists())

    def test_bar_scale_and_values(self):
        data=copy.deepcopy(self.data);data['slides']=data['slides'][:1]
        block={'type':'bars','description':'Synthetic test values; no business result.','maximum':100,'unit':'items','items':[{'label':'First','value':25},{'label':'Second','value':50}]}
        data['slides'][0]['blocks']=[block]
        result,dest=self.run_build(data);self.assertEqual(result.returncode,0,result.stderr)
        doc=Markup();doc.feed(dest.read_text())
        bars=[a for t,a in doc.tags if a.get('class')=='bar']
        self.assertEqual([float(a['width']) for a in bars],[165,330]);self.assertEqual({a['x'] for a in bars},{'280'})
        for i,value in enumerate((-1,101,float('inf'),True)):
            block['items'][0]['value']=value
            result,dest=self.run_build(data,output=f'bad-bar-{i}.html');self.assertEqual(result.returncode,2);self.assertFalse(dest.exists())

    def test_visual_strings_are_escaped(self):
        data=copy.deepcopy(self.data)
        data['slides'][4]['blocks'][0]['fields'][0]['value']='<img src=x onerror=alert(1)>'
        data['slides'][0]['blocks'][0]['nodes'][0]['label']='<script>x</script>'
        result,dest=self.run_build(data);self.assertEqual(result.returncode,0,result.stderr)
        doc=Markup();doc.feed(dest.read_text())
        self.assertFalse(any(t in ('img','script') for t,a in doc.tags))
        self.assertIn('<img src=x onerror=alert(1)>',doc.text)

if __name__=='__main__':unittest.main()
