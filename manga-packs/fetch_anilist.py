import json,sys,time,urllib.request
Q='''query($p:Int){Page(page:$p,perPage:50){pageInfo{hasNextPage}media(type:ANIME,format:TV,source:MANGA,sort:POPULARITY_DESC,isAdult:false){title{romaji english}startDate{year}endDate{year}status
relations{edges{relationType node{type format title{romaji english} volumes status startDate{year} endDate{year} staff(perPage:3,sort:RELEVANCE){edges{role node{name{full}}}}}}}}}}'''
out=[]
for p in range(1,int(sys.argv[1])+1):
    d=None
    for t in range(4):
        try:
            r=urllib.request.Request('https://graphql.anilist.co',json.dumps({'query':Q,'variables':{'p':p}}).encode(),{'Content-Type':'application/json','Accept':'application/json','User-Agent':'NovelReader-personal/1.0'})
            d=json.load(urllib.request.urlopen(r,timeout=30));break
        except Exception as e:
            print('retry',p,e,file=sys.stderr);time.sleep(6)
    if not d:break
    out+=d['data']['Page']['media']
    if not d['data']['Page']['pageInfo']['hasNextPage']:break
    time.sleep(1.5)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(len(out))
