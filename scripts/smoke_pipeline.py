# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
"""Synthetic integration test ONLY. Never install this model in the real app."""
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='freshcheck-smoke-') as d:
    tmp = Path(d)
    rows = []
    rng = np.random.default_rng(1)
    for group in range(12):
        for label in ['fresh','suspicious','spoiled']:
            path = tmp/f'{group}_{label}.png'
            Image.fromarray(rng.integers(0,256,(64,64,3),dtype=np.uint8)).save(path)
            rows.append(dict(path=path.name,label=label,food_type='SYNTHETIC_TEST_ONLY',group_id=str(group),source='generated_noise',license='CC0-1.0'))
    manifest = tmp/'manifest.csv'
    with manifest.open('w',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    def run(script,*args):
        subprocess.run([sys.executable,str(root/'ml'/script),*map(str,args)],check=True,cwd=root)
    run('prepare_data.py','--manifest',manifest,'--root',tmp,'--out',tmp/'processed')
    run('train.py','--data',tmp/'processed','--out',tmp/'artifacts','--epochs',1,'--fine-epochs',1,'--batch',4,'--alpha',.35,'--weights','none')
    run('export.py','--model',tmp/'artifacts/model.keras','--config',tmp/'artifacts/training_config.json',
        '--calibration',tmp/'processed/train.csv','--out',tmp/'export')
    for mode in ['float32','float16','int8']:
        run('evaluate.py','--model',tmp/f'export/food_{mode}.tflite','--manifest',tmp/'processed/test.csv','--out',tmp/f'{mode}.json')
print('PASS: synthetic split -> train -> fine-tune -> 3 exports -> 3 evaluations. Not a food accuracy result.')
