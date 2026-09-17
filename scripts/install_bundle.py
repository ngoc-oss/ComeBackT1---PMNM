# SPDX-License-Identifier: MIT
"""Install both supplied models into FreshCheck Android after verifying checksums."""
import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];src=Path(a.bundle);dst=root/'android/app/src/main/assets'
pairs=[('meat','published_meat.onnx','published_model_config.json'),('fruit','fruitq_float32.onnx','fruit_model_config.json')]
for folder,model,config in pairs:
 c=json.loads((src/folder/config).read_text(encoding='utf-8'))
 if c['labels']!=['fresh','suspicious','spoiled'] or c['runtime']!='onnx':raise ValueError('Unexpected model contract')
 if hashlib.sha256((src/folder/model).read_bytes()).hexdigest()!=c['model_sha256']:raise ValueError(f'Checksum mismatch: {model}')
for folder,model,config in pairs:
 for name in [model,config]:shutil.copy2(src/folder/name,dst/name)
for name in ['CC-BY-4.0.txt','Torchvision-BSD.txt','Phteven-MIT.txt']:shutil.copy2(root/'LICENSES'/name,dst/name)
shutil.copy2(root/'docs/FRUITQ.md',dst/'FRUITQ-NOTICE.md')
print('Installed meat and experimental fruit models. Build Android to package them.')
