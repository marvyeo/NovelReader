#!/usr/bin/env python3
"""NovelReader prep: one command replaces ~6 manual steps.
usage: python3 prep.py BOOK.pdf WORKDIR PACKDIR [series_prefix=sao]
Writes (prints only a 4-line summary, never book text):
  WORKDIR/chunks/cNN.txt  compact book text, lines <=1800 chars, ~45k chars (~11k tokens) per chunk
  WORKDIR/ids.txt         id|name|group|role|lastvol for every person in earlier packs (read once, ~2k tokens)
  WORKDIR/idmap.json      same, machine-readable (lib.py uses it to auto-register known ids)
  WORKDIR/cover.b64.txt   480x720 jpeg data URI
"""
import sys, os, re, json, glob, subprocess, io, base64, tempfile

pdf, work, packs = sys.argv[1], sys.argv[2], sys.argv[3]
prefix = sys.argv[4] if len(sys.argv) > 4 else 'sao'
os.makedirs(work + '/chunks', exist_ok=True)

# 1. text -> compact -> split long lines at sentence ends
raw = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True, encoding='utf-8').stdout
t = raw.replace('\x0c', '')
t = re.sub(r'(?<!\n)\n(?!\n)', ' ', t)
t = re.sub(r'[ \t]+', ' ', t)
lines = [l.strip() for l in re.sub(r'\n{2,}', '\n', t).split('\n') if l.strip()]
out = []
for l in lines:
    while len(l) > 1800:
        cut = max(l.rfind('. ', 0, 1800), l.rfind('? ', 0, 1800), l.rfind('! ', 0, 1800), l.rfind('” ', 0, 1800))
        cut = cut + 1 if cut > 400 else 1800
        out.append(l[:cut].strip()); l = l[cut:].strip()
    out.append(l)
for f in glob.glob(work + '/chunks/c*.txt'): os.remove(f)
chunks, cur, size = [], [], 0
for l in out:
    cur.append(l); size += len(l) + 1
    if size >= 45000: chunks.append(cur); cur, size = [], 0
if cur: chunks.append(cur)
for i, c in enumerate(chunks, 1):
    open(f'{work}/chunks/c{i:02d}.txt', 'w', encoding='utf-8').write('\n'.join(c) + '\n')
tot = sum(len(l) for l in out)

# 2. id map from earlier packs (never printed in full)
idm = {}
for p in sorted(glob.glob(f'{packs}/{prefix}-v[0-9][0-9].json')):
    d = json.load(open(p, encoding='utf-8')); v = d['volume']['n']
    for x in d['people']:
        e = idm.setdefault(x['id'], {})
        e.update(name=x['name'], group=x['group'], role=x.get('role', ''), last=v)
json.dump(idm, open(work + '/idmap.json', 'w', encoding='utf-8'), ensure_ascii=False)
open(work + '/ids.txt', 'w', encoding='utf-8').write(
    '\n'.join(f"{k}|{v['name']}|{v['group']}|{v['role']}|v{v['last']}" for k, v in idm.items()) + '\n')

# 3. cover (pdfimages, never pdftoppm)
cov = 'no'
try:
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['pdfimages', '-f', '1', '-l', '1', '-all', pdf, td + '/i'], check=True)
        fs = sorted(glob.glob(td + '/i*'), key=os.path.getsize)
        im = Image.open(fs[-1]).convert('RGB').resize((480, 720), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=82)
        open(work + '/cover.b64.txt', 'w').write('data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode())
        cov = 'yes'
except Exception as e:
    cov = f'FAILED ({e}); make it by hand'

print(f'text: {tot} chars (~{tot//4} tokens) in {len(chunks)} chunks of ~11k tokens: read with Read, one chunk per call')
print(f'ids: {len(idm)} people from earlier packs -> {work}/ids.txt')
print(f'cover: {cov}')
