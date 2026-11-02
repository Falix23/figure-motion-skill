import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class TimelineTests(unittest.TestCase):
    def setUp(self): self.d=json.loads((ROOT/'examples/input.json').read_text())
    def test_boundary_enters_next_step(self):
        self.assertEqual(b.step_at(self.d, 0),0)
        self.assertEqual(b.step_at(self.d, 2.999),0)
        self.assertEqual(b.step_at(self.d, 3),1)
        self.assertEqual(b.step_at(self.d, 999),3)
    def test_dangling_edge_rejected(self):
        self.d['edges'][0]['to']='missing'
        with self.assertRaises(ValueError): b.validate(self.d)
    def test_dangling_step_rejected(self):
        self.d['steps'][0]['nodes']=['missing']
        with self.assertRaises(ValueError): b.validate(self.d)
    def test_multinode_cycle_permitted(self):
        self.d['edges'].append({'id':'back','from':'answer','to':'question'})
        b.validate(self.d)
    def test_duration_and_coordinates(self):
        for value in [0,True,float('nan'),61]:
            d=copy.deepcopy(self.d);d['steps'][0]['duration']=value
            with self.assertRaises(ValueError): b.validate(d)
        self.d['nodes'][0]['x']=941
        with self.assertRaises(ValueError): b.validate(self.d)
    def test_payload_cannot_end_script(self):
        self.d['title']='</script><img src=x onerror=alert(1)>'
        html=b.build(self.d)
        self.assertNotIn(self.d['title'],html)
        self.assertIn('\\u003c/script>',html)
    def test_duplicate_ids(self):
        self.d['nodes'][1]['id']=self.d['nodes'][0]['id']
        with self.assertRaises(ValueError): b.validate(self.d)
if __name__=='__main__':unittest.main()
