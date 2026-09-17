# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE.
import argparse
import hashlib
import json
import shutil
from pathlib import Path

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--bundle',required=True,help='Folder containing meat_resnet50_int8.onnx and published_model_config.json')
    a=p.parse_args();folder=Path(a.bundle)
    model=folder/'meat_resnet50_int8.onnx'
    config=json.loads((folder/'published_model_config.json').read_text(encoding='utf-8'))
    if hashlib.sha256(model.read_bytes()).hexdigest()!=config['model_sha256']:raise SystemExit('Model hash mismatch')
    if config['labels']!=['fresh','suspicious','spoiled']:raise SystemExit('Wrong output mapping')
    root=Path(__file__).resolve().parents[1];assets=root/'android/app/src/main/assets'
    assets.mkdir(parents=True,exist_ok=True)
    shutil.copy2(model,assets/'published_meat.onnx')
    shutil.copy2(folder/'published_model_config.json',assets/'published_model_config.json')
    shutil.copy2(root/'LICENSES/Phteven-MIT.txt',assets/'Phteven-MIT.txt')
    print('Installed published ResNet-50 INT8. Build Android again. This model supports red meat only.')
