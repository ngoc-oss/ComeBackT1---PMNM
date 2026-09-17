# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import argparse
import hashlib
import json
import shutil
from pathlib import Path

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--export', default='artifacts/export')
    p.add_argument('--variant',choices=['int8','float16','float32'],default='int8')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    folder = Path(a.export)
    blob = (folder/f'food_{a.variant}.tflite').read_bytes()
    if len(blob) < 8 or blob[4:8] != b'TFL3': raise SystemExit('Invalid TFLite file')
    config = json.loads((folder/'model_config.json').read_text(encoding='utf-8'))
    config['model_sha256'] = hashlib.sha256(blob).hexdigest()
    config['variant'] = a.variant
    # Threshold is model-specific: require separate calibration for a different variant.
    if a.variant != 'int8':
        config['threshold_status'] = 'default_not_calibrated'
        config['threshold'] = .7
    dest = root/'android/app/src/main/assets'
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'food_model.tflite').write_bytes(blob)
    (dest/'model_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Installed {a.variant} to {dest}; status={config["status"]}')
