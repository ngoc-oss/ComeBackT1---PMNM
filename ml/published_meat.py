# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE.
"""Convert and evaluate the authors' published checkpoint; NEVER trains replacement weights."""
import argparse
import csv
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
import torch
from torchvision import models, transforms
import onnx
import onnxruntime as ort
from onnxruntime.quantization import CalibrationDataReader, quantize_static, QuantType, QuantFormat

COMMIT = 'b31e61f43f8c608f119d379daa5b76768b50c5b3'
CHECKPOINT_HASH = '777a6239b0948acbf9354f0734e21cfc5467dad7b4364435189830d7ff9c7d57'
LABELS = ['fresh','suspicious','spoiled']
PREPROCESS = transforms.Compose([transforms.Resize(256),transforms.CenterCrop(224)])

def save(path, data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def pixels(path):
    with Image.open(path) as im:
        return np.array(PREPROCESS(ImageOps.exif_transpose(im).convert('RGB')),dtype=np.float32)

def rows(folder):
    with (folder/'_classes.csv').open(encoding='utf-8-sig',newline='') as f:
        data = list(csv.DictReader(f,skipinitialspace=True))
    out = []
    for r in data:
        target = [int(r[x]) for x in ['Fresh','Half-Fresh','Spoiled']]
        if sum(target)!=1 or any(x not in (0,1) for x in target): raise ValueError('Invalid source label')
        path = (folder/r['filename']).resolve()
        if not path.is_relative_to(folder.resolve()): raise ValueError('Unsafe image path')
        out.append((path,target.index(1)))
    return out

class PublishedWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.register_buffer('mean',torch.tensor([.485,.456,.406]).reshape(1,3,1,1))
        self.register_buffer('std',torch.tensor([.229,.224,.225]).reshape(1,3,1,1))
    def forward(self, rgb):
        x = (rgb.permute(0,3,1,2)/255.0-self.mean)/self.std
        # Source code maps 0=Spoiled, 1=Half-Fresh, 2=Fresh. Canonical order differs.
        logits = self.model(x)[:,[2,1,0]]
        return torch.softmax(logits,dim=1)

class Calibration(CalibrationDataReader):
    def __init__(self, data):
        selected = []
        rng = np.random.default_rng(42)
        for label in range(3):
            candidates = [x for x in data if x[1]==label]
            rng.shuffle(candidates)
            selected.extend(candidates[:40])
        self.iterator = iter(selected)
    def get_next(self):
        item = next(self.iterator,None)
        return None if item is None else {'rgb':pixels(item[0])[None]}

def session(path):
    opts = ort.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
    return ort.InferenceSession(str(path),sess_options=opts,providers=['CPUExecutionProvider'])

def audit(train,test,out):
    seen = {}; conflicts=[]; duplicate_count=0; counts={}
    for split,data in [('train',train),('valid',test)]:
        counts[split] = dict(Counter(LABELS[y] for _,y in data))
        for path,y in data:
            with Image.open(path) as im:
                im=ImageOps.exif_transpose(im).convert('RGB')
                digest=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
            if digest in seen:
                duplicate_count+=1
                old=seen[digest]
                conflicts.append({'first':old[0],'second':path.name,'cross_split':old[1]!=split,
                                  'label_conflict':old[2]!=y})
            else:seen[digest]=(path.name,split,y)
    report={'source_split_counts':counts,'total_images':len(train)+len(test),'decoded_exact_duplicates':duplicate_count,
            'duplicates':conflicts,'group_ids_available':False,
            'limitations':'Original source split preserved. Physical specimen IDs absent; near-duplicate or specimen leakage not ruled out.'}
    save(out/'dataset_audit.json',report)
    return report

def evaluate(path,data,out):
    s=session(path);cm=np.zeros((3,3),dtype=int);times=[];scores=[];truth=[]
    for i,(file,y) in enumerate(data):
        x=pixels(file)[None]
        if i==0:
            for _ in range(10):s.run(None,{'rgb':x})
        start=time.perf_counter();p=s.run(None,{'rgb':x})[0][0];times.append((time.perf_counter()-start)*1000)
        cm[y,int(p.argmax())]+=1;scores.append(p.tolist());truth.append(y)
    precision=np.divide(np.diag(cm),cm.sum(0),out=np.zeros(3),where=cm.sum(0)!=0)
    recall=np.divide(np.diag(cm),cm.sum(1),out=np.zeros(3),where=cm.sum(1)!=0)
    f1=np.divide(2*precision*recall,precision+recall,out=np.zeros(3),where=precision+recall!=0)
    probs=np.array(scores);truth=np.array(truth);accepted=probs.max(1)>=.70
    report={'n':len(data),'labels':LABELS,'confusion_matrix':cm.tolist(),'accuracy':float(np.trace(cm)/cm.sum()),
        'macro_f1':float(f1.mean()),'precision':precision.tolist(),'recall':recall.tolist(),'f1':f1.tolist(),
        'spoiled_as_fresh_rate':float(cm[2,0]/cm[2].sum()),'threshold':.70,'threshold_status':'default_not_calibrated',
        'coverage':float(accepted.mean()),'accepted_accuracy':float((probs.argmax(1)[accepted]==truth[accepted]).mean()) if accepted.any() else None,
        'host_inference_ms':{'p50':float(np.percentile(times,50)),'p95':float(np.percentile(times,95))},
        'model_bytes':path.stat().st_size,'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'evaluation_scope':'Source valid split; no guarantee of unseen specimen independence. Not a phone benchmark, not authors paper metric.'}
    save(out/(path.stem+'_evaluation.json'),report)
    with (out/(path.stem+'_predictions.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['filename','truth','prediction','fresh','half_fresh','spoiled'])
        for (file,y),p in zip(data,probs):w.writerow([file.name,LABELS[y],LABELS[int(p.argmax())],*p.tolist()])
    return report

def main(a):
    torch.set_num_threads(4);torch.set_num_interop_threads(1)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    checkpoint=Path(a.checkpoint)
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=CHECKPOINT_HASH:raise ValueError('Checkpoint does not match verified authors file')
    data_root=Path(a.data)
    train,test=rows(data_root/'train'),rows(data_root/'valid')
    audit(train,test,out)
    m=models.resnet50(weights=None);m.fc=torch.nn.Linear(m.fc.in_features,3)
    m.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True),strict=True)
    wrapper=PublishedWrapper(m).eval()
    fp=out/'meat_resnet50_float32.onnx'
    x=torch.from_numpy(pixels(test[0][0])[None])
    torch.onnx.export(wrapper,x,str(fp),input_names=['rgb'],output_names=['probabilities'],
                      opset_version=17,dynamo=False)
    onnx.checker.check_model(str(fp))
    sess=session(fp);errors=[];matches=[]
    # Every comparison uses real held-out-source images and identical preprocessed tensors.
    for file,_ in test[:30]:
        x=pixels(file)[None]
        with torch.inference_mode():expected=wrapper(torch.from_numpy(x)).numpy()
        actual=sess.run(None,{'rgb':x})[0]
        errors.append(float(np.max(np.abs(expected-actual))));matches.append(bool(expected.argmax()==actual.argmax()))
    if max(errors)>1e-4 or not all(matches):raise ValueError('ONNX parity failed')
    save(out/'conversion_check.json',{'real_images':30,'max_probability_difference':max(errors),'same_argmax':all(matches),
        'checkpoint_sha256':CHECKPOINT_HASH,'authors_commit':COMMIT,'weights_retrained':False})
    q=out/'meat_resnet50_int8.onnx'
    quantize_static(str(fp),str(q),Calibration(train),quant_format=QuantFormat.QDQ,
                    activation_type=QuantType.QUInt8,weight_type=QuantType.QInt8,per_channel=True,
                    op_types_to_quantize=['Conv','MatMul','Gemm'])
    reports={}
    for path in [fp,q]:
        reports[path.stem]=evaluate(path,test,out)
        print(path.name,reports[path.stem],flush=True)
    # INT8 is the predeclared mobile artifact; no metric-driven checkpoint/threshold tuning here.
    config={'schema_version':1,'version':'0.2.0-phteven-int8','runtime':'onnx','labels':LABELS,
        'source_labels':['Spoiled','Half-Fresh','Fresh'],'output_reorder':[2,1,0],
        'input_size':224,'input_range':[0,255],'crop':'resize_shorter_256_center_224',
        'threshold':.70,'threshold_status':'default_not_calibrated','food_types':['Thịt đỏ — bộ dữ liệu Meat Freshness'],
        'model_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'status':'published_checkpoint_research_only',
        'paper':'https://arxiv.org/abs/2305.00986','authors_commit':COMMIT,
        'original_checkpoint_sha256':CHECKPOINT_HASH,'model_file':'published_meat.onnx'}
    save(out/'published_model_config.json',config)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True);p.add_argument('--data',required=True)
    p.add_argument('--out',default='artifacts/published')
    main(p.parse_args())
