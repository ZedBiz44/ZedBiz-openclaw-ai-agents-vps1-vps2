#!/usr/bin/env python3
"""Read only the bounded acceptance session; report tool receipts without page contents."""
import json, pathlib, re, sqlite3, sys
n, path = sys.argv[1:]
assert n in {'terry','edith','amanda','marsha','maggie','inga','gohzed','grogar','wilma','victor','vivian','harry','suzy','frank'}
key='agent:main:notion-search-acceptance-'+n+'-20260912'
searches=[]; pages=[]; failures=[]

def decoded_objects(value, depth=0):
    if depth>24:return
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from decoded_objects(child,depth+1)
    elif isinstance(value,list):
        for child in value:yield from decoded_objects(child,depth+1)
    elif isinstance(value,str):
        # Some container tool receipts retain escaped enhanced Markdown instead of
        # an outer page metadata object. Read only its first root page tag.
        normalized=re.sub(r'\\+(?=")','',value)
        tag=re.search(r'<page url="([^"]+)"',normalized)
        if tag:yield {'metadata':{'type':'page'},'url':tag.group(1),'proofSource':'enhanced-markdown-page-tag'}
        try: child=json.loads(value)
        except (ValueError,TypeError):return
        if isinstance(child,(dict,list)):yield from decoded_objects(child,depth+1)

with sqlite3.connect('file:'+str(pathlib.Path(path))+'?mode=ro',uri=True) as db:
    row=db.execute('select current_session_id from session_nodes where session_key=?',(key,)).fetchone()
    assert row, 'Acceptance session missing'
    for raw, in db.execute('select event_json from transcript_events where session_id=? order by seq',(row[0],)):
        m=json.loads(raw).get('message',{})
        if m.get('role')!='toolResult':continue
        tool=m.get('toolName','')
        if 'notion' not in tool:continue
        if m.get('isError'):failures.append(tool)
        for obj in decoded_objects(m):
            if isinstance(obj.get('results'),list) and obj.get('type') in {'ai_search','workspace_search'}:
                receipt={'tool':tool,'type':obj['type'],'count':len(obj['results']),'ids':[v.get('id') for v in obj['results']]}
                if receipt not in searches:searches.append(receipt)
            if tool.endswith('.fetch') and isinstance(obj.get('metadata'),dict) and obj['metadata'].get('type')=='page' and isinstance(obj.get('url'),str):
                if obj['url'] not in pages:pages.append(obj['url'])
ids={i.replace('-','').lower() for s in searches for i in s['ids'] if isinstance(i,str)}
opened=[p for p in pages if any(i in p.replace('-','').lower() for i in ids)]
result={'agent':n,'actualSearchReceipts':searches,'openedReturnedPages':opened,'notionToolFailures':failures,'passed':bool(searches and opened and all(s['type']=='ai_search' and s['count']>0 for s in searches) and not failures)}
print(json.dumps(result))
assert result['passed'], 'Actual search-and-fetch receipt did not pass'
