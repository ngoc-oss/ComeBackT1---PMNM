# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
"""Select abstention threshold using validation predictions only, never test."""
import argparse
import json
from pathlib import Path
import numpy as np
from common import save_json

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--validation-predictions', required=True)
    p.add_argument('--config', default='artifacts/export/model_config.json')
    p.add_argument('--min-accuracy', type=float, default=.90)
    p.add_argument('--min-coverage', type=float, default=.50)
    a = p.parse_args()
    config = json.loads(Path(a.config).read_text(encoding='utf-8'))
    evidence = json.loads(Path(a.validation_predictions).with_suffix('.json').read_text(encoding='utf-8'))
    if evidence['model_sha256'] != config['model_sha256']:
        raise SystemExit('Validation predictions and config are from different models')
    if not (0 <= a.min_accuracy <= 1 and 0 < a.min_coverage <= 1):
        p.error('Invalid target bounds')
    z = np.load(a.validation_predictions)
    probs, y = z['probabilities'], z['truth']
    candidates = []
    for threshold in np.linspace(.34,.99,66):
        mask = probs.max(1) >= threshold
        coverage = float(mask.mean())
        accuracy = float((probs.argmax(1)[mask]==y[mask]).mean()) if mask.any() else 0
        if coverage >= a.min_coverage and accuracy >= a.min_accuracy:
            candidates.append((coverage, accuracy, float(threshold)))
    if not candidates:
        raise SystemExit('No threshold meets validation targets. Improve data/model; config unchanged.')
    coverage, accuracy, threshold = max(candidates)
    config.update(threshold=threshold, threshold_status='selected_on_validation',
                  validation_coverage=coverage, validation_accepted_accuracy=accuracy,
                  validation_manifest_sha256=evidence['manifest_sha256'])
    save_json(a.config, config)
    print(f'threshold={threshold:.2f}; coverage={coverage:.3f}; accuracy={accuracy:.3f}')
