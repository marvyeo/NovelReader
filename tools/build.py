#!/usr/bin/env python3
"""usage: NR_IDMAP=WORK/idmap.json python3 build.py NOTES_MODULE OUT.json [WORK/cover.b64.txt]
Run from the folder holding lib.py and the notes modules. Validates, computes `from`, sorts, dumps.
Prints one summary line (never the pack)."""
import sys, json, importlib, datetime, os
sys.path.insert(0, os.getcwd())
mod, out = sys.argv[1], sys.argv[2]
cover = sys.argv[3] if len(sys.argv) > 3 else None
importlib.import_module(mod)
import lib
P, M = lib.P, lib.P['meta']
chs = sorted(P['chapters'], key=lambda c: c['n'])
nums = [c['n'] for c in chs]
assert nums == list(range(1, len(nums) + 1)), f'chapter numbers not 1..N: {nums}'
N = len(nums); people = []
for p in P['people'].values():
    allc = [c for c, *_ in p['facts'] + p['aka'] + p['status']]
    assert allc, f"{p['id']} has no facts/aka/status"
    assert all(1 <= c <= N for c in allc), f"{p['id']} has chapter outside 1..{N}"
    p['from'] = min(allc)
    for k in ('facts', 'aka', 'status'): p[k].sort(key=lambda x: x[0])
    people.append(p)
people.sort(key=lambda p: (p['from'], p['id']))
for t in P['terms'] + P['timeline']: assert 1 <= t['at'] <= N, t
known = {v['group'] for v in lib._IDM.values()}
new_groups = {p['group'] for p in people} - known
pack = {'format': 'novelreader-volume', 'formatVersion': 1,
        'series': {'id': M.get('series_id', 'sao'), 'title': M.get('title', 'Sword Art Online'), 'author': M.get('author', 'Reki Kawahara')},
        'volume': {'n': M['n'], 'subtitle': M['subtitle'], 'chapters': N, 'source': M.get('source', 'Yen Press eBook (Yen On)'),
                   'processedOn': datetime.date.today().isoformat()},
        'recap': M['recap'], 'chapters': chs, 'people': people, 'terms': P['terms'], 'timeline': sorted(P['timeline'], key=lambda x: x['at'])}
if cover and os.path.exists(cover): pack['cover'] = open(cover).read().strip()
s = json.dumps(pack, ensure_ascii=False)
open(out, 'w', encoding='utf-8').write(s)
nt = (len(s) - len(pack.get('cover', ''))) // 4
print(f"OK {out}: {N} chapters, {len(people)} people, {len(P['terms'])} terms, {len(P['timeline'])} timeline, notes ~{nt} tokens (target <=11k)"
      + (f"; NEW GROUPS: {sorted(new_groups)}" if new_groups else '') + ('' if 'cover' in pack else '; NO COVER'))
