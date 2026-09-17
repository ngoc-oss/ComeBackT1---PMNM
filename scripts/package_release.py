# SPDX-License-Identifier: MIT
# FreshCheck source is licensed under MIT; see LICENSE at repository root.
import argparse
import hashlib
from pathlib import Path
import re
import tarfile

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--version',default='0.5.1')
    a = p.parse_args()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-z0-9.]+)?',a.version): p.error('Invalid version')
    root = Path(__file__).resolve().parents[1]
    dest = root/'dist'; dest.mkdir(exist_ok=True)
    archive = dest/f'FreshCheck-{a.version}-source.tar.gz'
    excludes = {'.git','.gradle','.venv','__pycache__','build','dist','raw','processed','artifacts'}
    with tarfile.open(archive,'w:gz',format=tarfile.PAX_FORMAT) as tar:
        for file in sorted(root.rglob('*')):
            relative = file.relative_to(root)
            if not file.is_file() or file.is_symlink() or set(relative.parts) & excludes: continue
            if file.name in {'local.properties','model_config.json','manifest.csv'}: continue
            if file.suffix in {'.pyc','.jks','.keystore','.tflite','.pth','.npz'}: continue
            tar.add(file,arcname=f'FreshCheck-{a.version}/{relative.as_posix()}',recursive=False)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (dest/'SHA256SUMS').write_text(f'{digest}  {archive.name}\n',encoding='utf-8')
    print(archive)
