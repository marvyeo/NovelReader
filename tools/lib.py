"""NovelReader notes helpers. Notes modules do `from lib import *` and call these.
Known ids (from idmap.json) are auto-registered on first use of f/al/st, so person() is only
needed for NEW people. Keep notes terse: target <= 11k tokens of notes per volume.
  meta(n, subtitle, recap=[para,...])
  ch(n, title, where, summary, [points])           chapter / scene-chapter n
  person(id, name, group, role)                    new person (or override role of old one)
  f(id, ch, text)   fact        al(id, ch, text)   alias        st(id, ch, 'alive|dead|unknown', label)
  term(kind, name, at, text)    kind in concept|creature|item|place
  tl(at, when, what)            timeline item
"""
import json, os
P = dict(meta={}, chapters=[], people={}, terms=[], timeline=[])
_IDM = json.load(open(os.environ.get('NR_IDMAP', 'idmap.json'), encoding='utf-8')) if os.path.exists(os.environ.get('NR_IDMAP', 'idmap.json')) else {}

def meta(n, subtitle, recap, **kw): P['meta'] = dict(n=n, subtitle=subtitle, recap=recap, **kw)
def ch(n, title, where, summary, points=()): P['chapters'].append(dict(n=n, title=title, where=where, summary=summary, points=list(points)))

def person(id, name=None, group=None, role=None):
    p = P['people'].get(id)
    if p is None:
        old = _IDM.get(id, {})
        name, group = name or old.get('name'), group or old.get('group')
        if not (name and group): raise KeyError(f'new person {id!r} needs person(id, name, group, role)')
        p = P['people'][id] = dict(id=id, name=name, group=group, role=role if role is not None else old.get('role', ''), aka=[], facts=[], status=[])
    elif role is not None: p['role'] = role
    return p

def f(id, c, text): person(id)['facts'].append([c, text])
def al(id, c, text): person(id)['aka'].append([c, text])
def st(id, c, state, label=''):
    assert state in ('alive', 'dead', 'unknown'), state
    person(id)['status'].append([c, state, label])
def term(kind, name, at, text):
    assert kind in ('concept', 'creature', 'item', 'place'), kind
    P['terms'].append(dict(kind=kind, name=name, at=int(at), text=text))
def tl(at, when, what): P['timeline'].append(dict(at=int(at), when=when, what=what))
