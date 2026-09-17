# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import csv
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

LABELS = ['fresh', 'suspicious', 'spoiled']
SIZE = 224

def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def image_array(path):
    # Same center-square crop, RGB, bilinear resize as Android. Normalization is IN model.
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
        w, h = im.size
        side = min(w, h)
        left, top = (w-side)//2, (h-side)//2
        im = im.crop((left, top, left+side, top+side))
        return np.asarray(im.resize((SIZE, SIZE), Image.Resampling.BILINEAR), dtype=np.float32)

def encode_tensor(x, detail):
    dtype = detail['dtype']
    if np.issubdtype(dtype, np.integer):
        scale, zero = detail['quantization']
        if scale <= 0:
            raise ValueError('Missing quantization scale')
        limits = np.iinfo(dtype)
        return np.clip(np.rint(x / scale + zero), limits.min, limits.max).astype(dtype)
    return x.astype(dtype)

def decode_tensor(x, detail):
    if np.issubdtype(detail['dtype'], np.integer):
        scale, zero = detail['quantization']
        return (x.astype(np.float32) - zero) * scale
    return x.astype(np.float32)

def select_result(probabilities, threshold):
    p = np.asarray(probabilities)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError('Expected three finite probabilities')
    idx = int(p.argmax())
    return LABELS[idx] if p[idx] >= threshold else 'uncertain'
