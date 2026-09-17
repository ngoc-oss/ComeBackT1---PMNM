# SPDX-License-Identifier: MIT
"""Install the FreshCheck-trained FruQ-DB experiment alongside the meat model."""
import argparse, hashlib, json, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];src=Path(a.model_dir);dst=root/'android/app/src/main/assets'
c=json.loads((src/'fruit_model_config.json').read_text(encoding='utf-8'))
if c['model_file']!='fruitq_float32.onnx' or c['labels']!=['fresh','suspicious','spoiled']:raise ValueError('Unexpected model contract')
if hashlib.sha256((src/c['model_file']).read_bytes()).hexdigest()!=c['model_sha256']:raise ValueError('Model hash mismatch')
for name in [c['model_file'],'fruit_model_config.json']:shutil.copy2(src/name,dst/name)
shutil.copy2(root/'docs/FRUITQ.md',dst/'FRUITQ-NOTICE.md')
print('Installed experimental fruit model; published meat model retained.')
