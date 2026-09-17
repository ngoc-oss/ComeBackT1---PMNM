# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE.
"""Preserve real source labels and source split, without inventing physical specimen groups."""
import argparse,csv,hashlib,json
from pathlib import Path

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--out',default='data/published_index')
    a=p.parse_args();root=Path(a.data).resolve();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    fields=['path','source_label','label','food_type','source_split','group_id','source','license','sha256_file']
    mapping={'Fresh':'fresh','Half-Fresh':'suspicious','Spoiled':'spoiled'}
    for split in ['train','valid']:
        with (root/split/'_classes.csv').open(encoding='utf-8-sig',newline='') as f:data=list(csv.DictReader(f,skipinitialspace=True))
        with (out/f'source_{split}.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for r in data:
                labels=[x for x in mapping if r[x].strip()=='1']
                if len(labels)!=1:raise ValueError('Not exactly one source label')
                file=(root/split/r['filename']).resolve()
                if not file.is_relative_to(root):raise ValueError('Unsafe path')
                w.writerow(dict(path=str(file),source_label=labels[0],label=mapping[labels[0]],food_type='red_meat',
                    source_split=split,group_id='',source='https://www.kaggle.com/datasets/vinayakshanawad/meat-freshness-image-dataset',
                    license='CC0-1.0 (as declared by uploader)',sha256_file=hashlib.sha256(file.read_bytes()).hexdigest()))
    print('Indexed original splits. group_id intentionally empty: specimen IDs not supplied by source. Do not claim group-disjoint evaluation.')
