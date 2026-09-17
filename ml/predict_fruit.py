# SPDX-License-Identifier: MIT
"""Offline prediction with the FreshCheck fruit model, not the paper checkpoint."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import onnxruntime as ort
from fruitq import image_array,LABELS
p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--image',required=True);a=p.parse_args()
root=Path(a.model_dir);c=json.loads((root/'fruit_model_config.json').read_text(encoding='utf-8'));model=root/c['model_file']
if hashlib.sha256(model.read_bytes()).hexdigest()!=c['model_sha256']:raise ValueError('SHA256 mismatch')
opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
s=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
scores=s.run(None,{'rgb':image_array(a.image)[None]})[0][0];i=int(scores.argmax())
print(json.dumps({'label':LABELS[i] if scores[i]>=c['threshold'] else None,'scores':dict(zip(LABELS,map(float,scores))),'origin':c['checkpoint_origin'],'scope':'FruQ-DB experiment; not a food safety test'},ensure_ascii=False,indent=2))
