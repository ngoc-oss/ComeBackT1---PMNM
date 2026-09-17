# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE.
"""Single-image offline inference; needs numpy, Pillow and onnxruntime only."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import onnxruntime as ort

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--image',required=True)
    a=p.parse_args();folder=Path(a.bundle)
    config=json.loads((folder/'published_model_config.json').read_text(encoding='utf-8'))
    model=folder/'meat_resnet50_int8.onnx'
    if hashlib.sha256(model.read_bytes()).hexdigest()!=config['model_sha256']:raise SystemExit('Model SHA-256 mismatch')
    with Image.open(a.image) as im:
        im=ImageOps.exif_transpose(im).convert('RGB');w,h=im.size
        nw,nh=(256,int(h*256/w)) if w<=h else (int(w*256/h),256)
        im=im.resize((nw,nh),Image.Resampling.BILINEAR)
        left,top=round((nw-224)/2),round((nh-224)/2)
        x=np.array(im.crop((left,top,left+224,top+224)),dtype=np.float32)[None]
    opts=ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
    s=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
    scores=s.run(None,{'rgb':x})[0][0];index=int(scores.argmax())
    label=['TƯƠI','NGHI NGỜ (Half-Fresh)','HƯ'][index] if scores[index]>=config['threshold'] else 'CHƯA ĐỦ CƠ SỞ'
    print(json.dumps({'result':label,'scores':dict(zip(['Fresh','Half-Fresh','Spoiled'],map(float,scores))),
        'model_version':config['version'],'scope':'Red meat only; visual source labels, not food safety certification.'},ensure_ascii=False,indent=2))
