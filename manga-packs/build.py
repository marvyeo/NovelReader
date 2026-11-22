import json,glob,re,sys
rows={};dups=[]
for f in sorted(glob.glob('src/*.txt')):
    for ln in open(f,encoding='utf-8'):
        ln=ln.strip()
        if not ln or ln.startswith('#'):continue
        p=[x.strip() for x in ln.split('|')]
        if len(p)!=5: print('BAD',f,ln);continue
        t,a,v,an,mg=p
        if any(x in('—','dup','-') or x.startswith('dup') for x in (an,mg)) or t.endswith('dup)') or 'dup' in t.lower().split():print('SKIP',t);continue
        k=re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
        if k in rows: dups.append(t);continue
        ong=mg.endswith('-') or mg.lower().endswith('present')
        mg2=mg.rstrip('-')+'–present' if mg.endswith('-') else mg
        rows[k]={'title':t,'author':a,'status':'new','total':int(v or 0),'ongoing':ong,'note':f'Anime: {an} · Manga: {mg2}'}
out=sorted(rows.values(),key=lambda m:re.sub(r'^(the )','',m['title'].lower()))
json.dump({'format':'novelreader-manga','manga':out},open('manga-anime-pack.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(out),'entries; dups skipped:',dups)
