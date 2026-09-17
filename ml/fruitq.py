# SPDX-License-Identifier: MIT
# FreshCheck implementation; dataset is CC BY 4.0, see docs/FRUITQ.md.
"""Reproducible experimental classifier on the published FruQ-DB labels.
This is NOT the checkpoint or an exact reproduction of the FruitQ paper.
"""
import argparse, csv, hashlib, json, random, time, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

LABELS = ['fresh', 'suspicious', 'spoiled']
SOURCE_LABELS = {'fresh': 0, 'mild': 1, 'rotten': 2}
ARCHIVE_MD5 = '1a942c2d49dc302bacef155561e1f9a8'

def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def image_array(path):
    with Image.open(path) as im:
        return np.asarray(ImageOps.exif_transpose(im).convert('RGB').resize((224,224), Image.Resampling.BILINEAR), dtype=np.float32)

def prepare(archive, dest, output):
    archive, dest, output = Path(archive), Path(dest), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    digest = hashlib.md5(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_MD5:
        raise ValueError(f'Archive MD5 mismatch: {digest}')
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for f in z.infolist():
            target = (dest / f.filename).resolve()
            if not target.is_relative_to(dest.resolve()): raise ValueError('Unsafe ZIP path')
        z.extractall(dest)
    rows, seen, duplicates = [], {}, []
    for p in sorted(dest.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.jpg','.jpeg','.png','.bmp'}: continue
        parts = [v.lower() for v in p.relative_to(dest).parts[:-1]]
        matches = [v for v in parts if v in SOURCE_LABELS]
        if len(matches) != 1: raise ValueError(f'Unrecognized class folder: {p}')
        name = matches[0]
        with Image.open(p) as im:
            rgb = im.convert('RGB')
            pixel_hash = hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()
        row = dict(path=p.relative_to(dest).as_posix(),source_label=name,label=LABELS[SOURCE_LABELS[name]],label_id=SOURCE_LABELS[name],pixel_sha256=pixel_hash,source_group_id='')
        if pixel_hash in seen:
            if seen[pixel_hash]['label'] != row['label']: raise ValueError('Identical image has conflicting labels')
            duplicates.append(row); continue
        seen[pixel_hash] = row; rows.append(row)
    if not rows or set(r['source_label'] for r in rows) != set(SOURCE_LABELS): raise ValueError('All three source labels are required')
    rng = random.Random(2026)
    for label in range(3):
        group = [r for r in rows if r['label_id']==label]; rng.shuffle(group)
        n = len(group); a, b = int(.7*n), int(.85*n)
        for i,r in enumerate(group): r['split'] = 'train' if i<a else 'validation' if i<b else 'test'
    rows.sort(key=lambda r:r['path'])
    with (output/'manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    audit = {'archive_md5':digest,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'raw_images':len(rows)+len(duplicates),'unique_images':len(rows),'removed_exact_duplicates':len(duplicates),'counts_unique':dict(Counter(r['source_label'] for r in rows)),'counts_original':dict(Counter(r['source_label'] for r in rows+duplicates)),'split_counts':dict(Counter(r['split'] for r in rows)), 'split_protocol':'seed2026; stratified 70/15/15 after exact decoded-pixel deduplication; FRAME split only', 'limitation':'No specimen/video identifiers verified. Adjacent video frames may cross splits. Test is internal diagnostic, NOT independent field validation.'}
    dump(output/'audit.json',audit);dump(output/'excluded_duplicates.json',duplicates)
    print(json.dumps(audit,ensure_ascii=False),flush=True)
    return rows

def metrics(probs, ys):
    pred=probs.argmax(1); cm=np.zeros((3,3),dtype=int)
    for y,p in zip(ys,pred): cm[y,p]+=1
    precision=np.diag(cm)/np.maximum(cm.sum(0),1);recall=np.diag(cm)/np.maximum(cm.sum(1),1)
    f1=2*precision*recall/np.maximum(precision+recall,1e-12)
    accepted=probs.max(1)>=.70
    return dict(n=len(ys),accuracy=float((pred==ys).mean()),macro_f1=float(f1.mean()),confusion_matrix=cm.tolist(),precision=precision.tolist(),recall=recall.tolist(),f1=f1.tolist(),spoiled_predicted_fresh=int(cm[2,0]),threshold=.70,coverage=float(accepted.mean()),accepted_accuracy=float((pred[accepted]==ys[accepted]).mean()) if accepted.any() else None)

def train(data, output, epochs):
    import torch
    from torch import nn
    from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
    torch.set_num_threads(4); torch.manual_seed(2026);np.random.seed(2026)
    output=Path(output);data=Path(data)
    with (output/'manifest.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    mean=torch.tensor([.485,.456,.406]).reshape(1,3,1,1);std=torch.tensor([.229,.224,.225]).reshape(1,3,1,1)
    net=mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    net.classifier=nn.Identity();net.eval()
    features=[]
    with torch.inference_mode():
        for i in range(0,len(rows),32):
            a=np.stack([image_array(data/r['path']) for r in rows[i:i+32]])
            x=torch.from_numpy(a).permute(0,3,1,2)/255
            features.append(net((x-mean)/std))
            if i%320==0: print(f'features {i}/{len(rows)}',flush=True)
    x=torch.cat(features).clone();ys=torch.tensor([int(r['label_id']) for r in rows])
    masks={s:torch.tensor([r['split']==s for r in rows]) for s in ['train','validation','test']}
    head=nn.Linear(576,3)
    opt=torch.optim.AdamW(head.parameters(),lr=.003,weight_decay=.01)
    counts=torch.bincount(ys[masks['train']],minlength=3).float()
    loss_fn=nn.CrossEntropyLoss(weight=counts.sum()/(3*counts))
    best=-1;best_state=None;log=[]
    for epoch in range(epochs):
        head.train();ids=torch.where(masks['train'])[0];ids=ids[torch.randperm(len(ids))]
        losses=[]
        for ix in ids.split(128):
            opt.zero_grad();loss=loss_fn(head(x[ix]),ys[ix]);loss.backward();opt.step();losses.append(loss.item())
        head.eval()
        with torch.no_grad(): v=metrics(head(x[masks['validation']]).softmax(-1).numpy(),ys[masks['validation']].numpy())
        log.append({'epoch':epoch+1,'loss':float(np.mean(losses)),'validation_macro_f1':v['macro_f1']})
        if v['macro_f1']>best:
            best=v['macro_f1'];best_state={k:v.clone() for k,v in head.state_dict().items()};best_epoch=epoch+1
        if epoch%10==0: print(log[-1],flush=True)
    head.load_state_dict(best_state);net.classifier=head;net.eval()
    torch.save(net.state_dict(),output/'fruitq_mobilenet_v3_small.pth')
    dump(output/'training.json',{'seed':2026,'epochs':epochs,'selected_epoch':best_epoch,'selection':'validation macro-F1 only','backbone':'torchvision MobileNetV3 Small ImageNet1K V1 frozen','training':'Only linear 576->3 head trained; no fine-tuning or synthetic images','preprocessing':'EXIF transpose, RGB, stretch resize224 bilinear, /255 ImageNet mean/std','log':log})
    class Export(nn.Module):
        def __init__(self,model):
            super().__init__();self.model=model;self.register_buffer('mean',mean);self.register_buffer('std',std)
        def forward(self,rgb): return self.model((rgb.permute(0,3,1,2)/255-self.mean)/self.std).softmax(-1)
    wrapped=Export(net).eval()
    torch.onnx.export(wrapped,torch.zeros(1,224,224,3),str(output/'fruitq_float32.onnx'),input_names=['rgb'],output_names=['probabilities'],opset_version=17,dynamo=False)
    import onnxruntime as ort
    from onnxruntime.quantization import CalibrationDataReader, quantize_static, QuantFormat, QuantType
    train_rows=[r for r in rows if r['split']=='train'];random.Random(2026).shuffle(train_rows)
    class Reader(CalibrationDataReader):
        def __init__(self): self.it=iter(train_rows[:120])
        def get_next(self):
            r=next(self.it,None)
            return None if r is None else {'rgb':image_array(data/r['path'])[None]}
    quantize_static(str(output/'fruitq_float32.onnx'),str(output/'fruitq_int8.onnx'),Reader(),quant_format=QuantFormat.QDQ,activation_type=QuantType.QUInt8,weight_type=QuantType.QInt8,per_channel=True,op_types_to_quantize=['Conv','MatMul','Gemm'])
    test_rows=[r for r in rows if r['split']=='test']; options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1
    for name in ['fruitq_float32','fruitq_int8']:
        session=ort.InferenceSession(str(output/f'{name}.onnx'),sess_options=options,providers=['CPUExecutionProvider']);predictions=[];times=[];parity=[]
        for i,r in enumerate(test_rows):
            a=image_array(data/r['path'])[None]
            if i==0:
                for _ in range(10): session.run(None,{'rgb':a})
            start=time.perf_counter();p=session.run(None,{'rgb':a})[0][0];times.append((time.perf_counter()-start)*1000);predictions.append(p)
            if name=='fruitq_float32' and i<30:
                with torch.no_grad(): pt=wrapped(torch.from_numpy(a)).numpy()[0]
                parity.append(float(np.max(np.abs(pt-p))))
        report=metrics(np.asarray(predictions),np.array([int(r['label_id']) for r in test_rows]));report.update(model_bytes=(output/f'{name}.onnx').stat().st_size,host_cpu_inference_ms_p50=float(np.percentile(times,50)),host_cpu_inference_ms_p95=float(np.percentile(times,95)),device_tested=False,evaluation_scope='Internal frame split; video leakage possible; not independent generalization',sha256=hashlib.sha256((output/f'{name}.onnx').read_bytes()).hexdigest())
        if parity: report['torch_onnx_max_probability_error_30_images']=max(parity)
        dump(output/f'{name}_evaluation.json',report)
        with (output/f'{name}_predictions.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['path','true_label','predicted_label',*LABELS])
            for r,p in zip(test_rows,predictions):w.writerow([r['path'],r['label'],LABELS[int(p.argmax())],*p.tolist()])
        print(name,report,flush=True)
    # Ship FP32 to avoid choosing quantization on the test set. INT8 remains a comparison artifact.
    fp=json.loads((output/'fruitq_float32_evaluation.json').read_text())
    dump(output/'fruit_model_config.json',{'schema_version':1,'runtime':'onnx','version':'fruitq-project-0.3.0-experimental','model_sha256':fp['sha256'],'labels':LABELS,'food_types':['Nhóm quả FruQ-DB (thử nghiệm)'],'threshold':.70,'input_size':224,'crop':'stretch_224','model_file':'fruitq_float32.onnx','checkpoint_origin':'Trained by FreshCheck, NOT released by authors of the FruitQ paper','dataset_doi':'10.5281/zenodo.7224690'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive');p.add_argument('--data',required=True);p.add_argument('--output',required=True);p.add_argument('--epochs',type=int,default=80);p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
    if a.archive: prepare(a.archive,a.data,a.output)
    if not a.prepare_only: train(a.data,a.output,a.epochs)
