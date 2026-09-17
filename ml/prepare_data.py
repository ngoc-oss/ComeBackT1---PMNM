# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
"""Validate provenance, decode/deduplicate images, split by physical specimen group."""
import argparse
import csv
import hashlib
from pathlib import Path
from collections import Counter
from sklearn.model_selection import GroupShuffleSplit
from PIL import Image, ImageOps
from common import LABELS, read_rows, save_json

REQUIRED = {'path', 'label', 'food_type', 'group_id', 'source', 'license'}

def prepare(manifest, root, output, seed=42):
    root, output = Path(root).resolve(), Path(output)
    rows = read_rows(manifest)
    if not rows or not REQUIRED.issubset(rows[0]):
        raise ValueError(f'Manifest requires {sorted(REQUIRED)}')
    clean, seen, duplicates = [], {}, []
    for row in rows:
        if any(not row.get(k, '').strip() for k in REQUIRED):
            raise ValueError(f'Empty required field: {row}')
        if row['label'] not in LABELS:
            raise ValueError(f'Unknown label: {row["label"]}')
        path = (root / row['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Image path outside dataset root')
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert('RGB')
            if min(im.size) < 64:
                raise ValueError(f'Image too small: {path}')
            digest = hashlib.sha256(str(im.size).encode() + im.tobytes()).hexdigest()
        if digest in seen:
            if seen[digest]['label'] != row['label']:
                raise ValueError(f'Conflicting labels on identical image: {path}')
            duplicates.append(row['path'])
            continue
        row = {**row, 'path': str(path), 'sha256_pixels': digest}
        seen[digest] = row
        clean.append(row)
    # Pick deterministic group-only partition with every class in every split.
    # No metric or model performance is used to select the partition.
    groups = [r['group_id'] for r in clean]
    chosen = None
    for attempt in range(200):
        splitter = GroupShuffleSplit(n_splits=1, test_size=.30, random_state=seed+attempt)
        train, hold = next(splitter.split(clean, groups=groups))
        hold_rows = [clean[i] for i in hold]
        try:
            v, t = next(GroupShuffleSplit(n_splits=1, test_size=.5, random_state=seed+attempt).split(
                hold_rows, groups=[r['group_id'] for r in hold_rows]))
        except ValueError:
            continue
        parts = {'train': [clean[i] for i in train], 'val': [hold_rows[i] for i in v],
                 'test': [hold_rows[i] for i in t]}
        if all(set(r['label'] for r in part) == set(LABELS) for part in parts.values()):
            chosen = parts
            break
    if chosen is None:
        raise ValueError('Cannot create three group-disjoint splits containing all labels. Collect more independent groups.')
    output.mkdir(parents=True, exist_ok=True)
    for split, part in chosen.items():
        with (output / f'{split}.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(part[0]))
            writer.writeheader()
            writer.writerows(part)
    report = {'seed_used': seed+attempt, 'duplicates_removed': duplicates,
              'splits': {s: {'images': len(p), 'groups': len(set(r['group_id'] for r in p)),
                              'labels': dict(Counter(r['label'] for r in p)),
                              'food_types': dict(Counter(r['food_type'] for r in p))}
                         for s, p in chosen.items()},
              'note': 'Exact decoded-pixel deduplication only. Review near duplicates and shared specimens manually.'}
    save_json(output/'dataset_report.json', report)
    return chosen

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--manifest', required=True)
    p.add_argument('--root', required=True)
    p.add_argument('--out', default='data/processed')
    p.add_argument('--seed', type=int, default=42)
    a = p.parse_args()
    prepare(a.manifest, a.root, a.out, a.seed)
