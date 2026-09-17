# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import argparse
import hashlib
import time
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from common import LABELS, read_rows, image_array, encode_tensor, decode_tensor, save_json

def evaluate(model_path, manifest, out, threshold=.7):
    rows = read_rows(manifest)
    if not rows:
        raise ValueError('Empty evaluation set')
    interpreter = tf.lite.Interpreter(model_path=str(model_path), num_threads=4)
    interpreter.allocate_tensors()
    inp, output = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    probabilities, times, truth = [], [], []
    for i, row in enumerate(rows):
        x = encode_tensor(image_array(row['path'])[None], inp)
        interpreter.set_tensor(inp['index'], x)
        if i == 0:
            for _ in range(10):
                interpreter.invoke()
        start = time.perf_counter()
        interpreter.invoke()
        times.append((time.perf_counter()-start)*1000)
        probabilities.append(decode_tensor(interpreter.get_tensor(output['index'])[0], output))
        truth.append(LABELS.index(row['label']))
    probs, truth = np.array(probabilities), np.array(truth)
    pred = probs.argmax(1)
    accepted = probs.max(1) >= threshold
    result = {'model_sha256': hashlib.sha256(Path(model_path).read_bytes()).hexdigest(),
        'manifest_sha256': hashlib.sha256(Path(manifest).read_bytes()).hexdigest(),
        'samples': len(rows), 'labels': LABELS, 'accuracy': accuracy_score(truth,pred),
        'macro_f1': f1_score(truth,pred,labels=[0,1,2],average='macro',zero_division=0),
        'report': classification_report(truth,pred,labels=[0,1,2],target_names=LABELS,output_dict=True,zero_division=0),
        'confusion_matrix': confusion_matrix(truth,pred,labels=[0,1,2]).tolist(),
        'spoiled_as_fresh_rate': float(np.mean(pred[truth==2] == 0)) if np.any(truth==2) else None,
        'threshold': threshold, 'coverage': float(accepted.mean()),
        'accepted_accuracy': float((pred[accepted]==truth[accepted]).mean()) if accepted.any() else None,
        'host_inference_ms': {'p50': float(np.percentile(times,50)), 'p95': float(np.percentile(times,95))},
        'model_bytes': Path(model_path).stat().st_size,
        'note': 'Host latency only; not a phone benchmark. Softmax scores are not safety probabilities.',
        'by_food_type': {}}
    for food in sorted(set(r['food_type'] for r in rows)):
        mask = np.array([r['food_type']==food for r in rows])
        result['by_food_type'][food] = {'n': int(mask.sum()), 'accuracy': float((truth[mask]==pred[mask]).mean())}
    save_json(out, result)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    np.savez(Path(out).with_suffix('.npz'), probabilities=probs, truth=truth)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
    ConfusionMatrixDisplay(np.array(result['confusion_matrix']), display_labels=LABELS).plot(cmap='Greens')
    plt.tight_layout()
    plt.savefig(Path(out).with_suffix('.png'), dpi=160)
    plt.close()
    print(result)
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--manifest', default='data/processed/test.csv')
    p.add_argument('--out', default='reports/evaluation.json')
    p.add_argument('--threshold', type=float, default=.7)
    a = p.parse_args()
    if not 0 <= a.threshold <= 1:
        p.error('threshold must be in [0,1]')
    evaluate(a.model, a.manifest, a.out, a.threshold)
