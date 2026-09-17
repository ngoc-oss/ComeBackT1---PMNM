# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import csv
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from common import image_array, encode_tensor, decode_tensor, select_result
from prepare_data import prepare

class PipelineTest(unittest.TestCase):
    def test_quantization_round_trip(self):
        for dtype,zero in [(np.uint8,0),(np.int8,-128)]:
            d = {'dtype':dtype,'quantization':(1.0,zero)}
            x = np.array([0,127,255],dtype=np.float32)
            np.testing.assert_allclose(decode_tensor(encode_tensor(x,d),d),x)

    def test_quantization_clamps_not_wraps(self):
        d = {'dtype':np.uint8,'quantization':(.5,0)}
        np.testing.assert_array_equal(encode_tensor(np.array([-100.,1000.]),d),[0,255])

    def test_uncertainty_not_suspicious(self):
        self.assertEqual(select_result([.3,.4,.3],.7),'uncertain')
        self.assertEqual(select_result([.1,.8,.1],.7),'suspicious')

    def test_invalid_scores_rejected(self):
        with self.assertRaises(ValueError): select_result([float('nan'),0,1],.7)

    def test_center_crop_rgb(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'a.png'
            im = np.zeros((80,160,3),dtype=np.uint8)
            im[:,40:120] = [255,0,0]
            Image.fromarray(im).save(p)
            x = image_array(p)
            self.assertEqual(x.shape,(224,224,3))
            np.testing.assert_array_equal(x[0,0],[255,0,0])

    def fixture(self,root):
        rows = []
        rng = np.random.default_rng(1)
        for group in range(20):
            for label in ['fresh','suspicious','spoiled']:
                p = root/f'{group}_{label}.png'
                Image.fromarray(rng.integers(0,256,(64,64,3),dtype=np.uint8)).save(p)
                rows.append(dict(path=p.name,label=label,food_type='test_only',group_id=str(group),source='synthetic',license='CC0-1.0'))
        return rows

    def write_manifest(self, root, rows):
        p = root/'manifest.csv'
        with p.open('w',newline='') as f:
            w = csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        return p

    def test_group_split_and_deduplication(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rows = self.fixture(root); rows.append(dict(rows[0]))
            parts = prepare(self.write_manifest(root,rows),root,root/'out')
            groups = {s:set(r['group_id'] for r in p) for s,p in parts.items()}
            self.assertFalse(groups['train'] & groups['val'])
            self.assertFalse(groups['train'] & groups['test'])
            self.assertFalse(groups['test'] & groups['val'])
            self.assertEqual(sum(len(p) for p in parts.values()),60)

    def test_conflicting_label_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rows = self.fixture(root)
            rows.append({**rows[0],'label':'spoiled'})
            with self.assertRaises(ValueError): prepare(self.write_manifest(root,rows),root,root/'out')

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); rows = self.fixture(root); rows[0]['path'] = '../outside.jpg'
            with self.assertRaises(ValueError): prepare(self.write_manifest(root,rows),root,root/'out')

if __name__ == '__main__': unittest.main()
