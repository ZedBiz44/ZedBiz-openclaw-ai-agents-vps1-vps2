#!/usr/bin/env python3
"""Read-only journal recall from Rocky's three approved current provider banks."""
import argparse,datetime,json,urllib.request,urllib.parse,concurrent.futures
BANKS=('rocky-vps4-discord','rocky-vps4-telegram','rocky-vps4-webchat')
BASE='http://127.0.0.1:9077'
def recall(bank,query):
    req=urllib.request.Request(BASE+'/v1/default/banks/'+urllib.parse.quote(bank,safe='')+'/memories/recall',data=json.dumps({'query':query[:1600],'budget':'mid','max_tokens':1800,'types':['world','experience','observation'],'query_timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}).encode(),headers={'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=65) as r: data=json.load(r)
        return {'bank':bank,'ok':True,'results':[{k:x.get(k) for k in ('id','text','occurred_start','occurred_end','mentioned_at','document_id')} for x in data.get('results',[])[:8]]}
    except Exception as e:return {'bank':bank,'ok':False,'error':str(e)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--query',required=True);p.add_argument('--counts-only',action='store_true');a=p.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(lambda bank:recall(bank,a.query),BANKS))
    if a.counts_only:rows=[{**{k:v for k,v in x.items() if k!='results'},'count':len(x.get('results',[]))} for x in rows]
    print(json.dumps({'provider':'hindsight','mode':'read-only-current-provider-banks','banks':rows},ensure_ascii=False))
    raise SystemExit(0 if all(x['ok'] for x in rows) else 1)
