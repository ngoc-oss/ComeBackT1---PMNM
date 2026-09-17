# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
from common import image_array, read_rows, save_json, LABELS

def main(a):
    model = tf.keras.models.load_model(a.model, compile=False)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = read_rows(a.calibration)
    rng = np.random.default_rng(42)
    # Balanced calibration from TRAIN ONLY, 100 images per class at most.
    calibration = []
    for label in LABELS:
        subset = [r for r in rows if r['label'] == label]
        if not subset:
            raise ValueError(f'Calibration missing {label}')
        rng.shuffle(subset)
        calibration.extend(subset[:100])
    def representative():
        for row in calibration:
            yield [image_array(row['path'])[None]]
    # SavedModel route avoids Keras variable conversion pitfalls.
    model.export(str(out/'saved_model'))
    for mode in ['float32', 'float16', 'int8']:
        c = tf.lite.TFLiteConverter.from_saved_model(str(out/'saved_model'))
        if mode == 'float16':
            c.optimizations = [tf.lite.Optimize.DEFAULT]
            c.target_spec.supported_types = [tf.float16]
        elif mode == 'int8':
            c.optimizations = [tf.lite.Optimize.DEFAULT]
            c.representative_dataset = representative
            c.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            c.inference_input_type = tf.uint8
            c.inference_output_type = tf.uint8
        blob = c.convert()
        (out/f'food_{mode}.tflite').write_bytes(blob)
    config = json.loads(Path(a.config).read_text(encoding='utf-8'))
    blob = (out/'food_int8.tflite').read_bytes()
    save_json(out/'model_config.json', {'schema_version': 1, 'version': a.version,
        'labels': LABELS, 'input_size': 224, 'input_range': [0,255],
        'crop': 'center_square', 'threshold': .70, 'threshold_status': 'default_not_calibrated',
        'food_types': config['food_types'], 'model_sha256': hashlib.sha256(blob).hexdigest(),
        'status': 'research_unvalidated', 'model_file': 'food_model.tflite'})
    print('Export complete. Evaluate and calibrate before installing assets.')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--model', default='artifacts/model.keras')
    p.add_argument('--config', default='artifacts/training_config.json')
    p.add_argument('--calibration', default='data/processed/train.csv')
    p.add_argument('--out', default='artifacts/export')
    p.add_argument('--version', default='0.1.0')
    main(p.parse_args())
