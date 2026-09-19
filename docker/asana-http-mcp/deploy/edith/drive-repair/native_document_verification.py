"""Compare every Google Docs tab using native-copy DOCX exports.

Exports are private verification artifacts, not replacement Drive documents.
All package entries except document properties must match. Unexpected export
differences stop verification; this module never retries or changes Drive files.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone

MIME='application/vnd.google-apps.document'

def package_content(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None or 'word/document.xml' not in z.namelist():
            raise ValueError('Invalid native document export')
        return {n:hashlib.sha256(z.read(n)).hexdigest() for n in sorted(z.namelist())
                if not n.endswith('/') and not n.startswith('docProps/')}

def tabs(base,fid):
    r=subprocess.run(['gog','docs','list-tabs',fid,'--account','jack@zbiz.work','--json','--no-input','--readonly'],capture_output=True,text=True,timeout=90)
    if r.returncode:raise ValueError('Native document tab listing failed: '+r.stderr[:300])
    data=json.loads(r.stdout)
    with (base/'native-read-receipts.jsonl').open('a') as log:
        log.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'action':'list-tabs','file_id':fid,'result':data})+'\n')
    result=data.get('tabs')
    if not isinstance(result,list) or not result:raise ValueError('Missing native document tabs')
    if any(not x.get('id') or 'title' not in x or 'index' not in x for x in result):raise ValueError('Unexpected native tab schema')
    return result

def verify_native(base,source,destination,gog):
    base=Path(base)
    if source.get('mimeType')!=MIME or destination.get('mimeType')!=MIME:raise ValueError('Native document type changed')
    a=tabs(base,source['id']);b=tabs(base,destination['id'])
    # Fail closed on changed topology, including parent/child tab attributes.
    signature=lambda values:[{k:v for k,v in x.items() if k!='id'} for x in values]
    if signature(a)!=signature(b):raise ValueError('Native tab topology changed')
    cache=base/'cache';cache.mkdir(exist_ok=True)
    matches=[]
    for index,(left,right) in enumerate(zip(a,b)):
        files=[]
        for obj,tab in [(source,left),(destination,right)]:
            out=cache/(obj['id']+'-tab-'+str(index)+'-verification.docx')
            gog('download',obj['id'],'--format','docx','--tab',tab['id'],'--out',str(out),'--overwrite')
            files.append(out)
        aa,bb=map(package_content,files)
        if aa!=bb:raise ValueError('Native exported content or formatting differs in tab '+str(index))
        matches.append({'tab_index':index,'title':left['title'],'package_parts':aa,'source_export':str(files[0]),'copy_export':str(files[1])})
    receipt=base/(source['id']+'-native-comparison.json')
    receipt.write_text(json.dumps({'source_id':source['id'],'active_id':destination['id'],'all_tabs_verified':True,'verified_at':datetime.now(timezone.utc).isoformat(),'comparisons':matches},indent=2))
    return 'All native Google Docs tabs exported and package content compared; original and active copy remain native Google Docs.',str(receipt)

