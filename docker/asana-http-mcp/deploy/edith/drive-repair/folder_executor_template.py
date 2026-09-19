import sys,pathlib,json,hashlib,zipfile,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
POOL=ThreadPoolExecutor(max_workers=3)
sys.path.insert(0,'/home/node/.openclaw/private/folder-cleanup/albertawide');import work
P=pathlib.Path(__file__).parent
registry=json.loads((P/'registry.json').read_text())
assert len(registry['clients'])==1
scope=next(iter(registry['clients'].values()))
work.P=P;ROOT=work.ROOT=scope['client_root_folder_id'];DRIVE=work.DRIVE
assert scope['shared_drive_id']==DRIVE
get=work.get;gog=work.gog;save=work.save;now=work.now
plan=json.loads((P/'prewrite-plan.json').read_text());before=json.loads((P/'initial-inventory.json').read_text());orig={x['id']:x for x in before['items']}
statepath=P/'execution-state.json';state=json.loads(statepath.read_text()) if statepath.exists() else {'folders':{},'copies':{},'pending':{},'archived':[]}
def persist():
 from execution_guard import save as atomic_save
 atomic_save(statepath,state)
def sig(p):
 assert not p.get('nextPageToken')
 return sorted((x.get('id'),x.get('type'),x.get('role')) for x in p.get('permissions',[]))
if (P/'root-permissions.json').exists():rp=json.loads((P/'root-permissions.json').read_text())
else:rp=gog('permissions',ROOT);save('root-permissions.json',rp)
def mutate(*args):
 if not state.get('first_write_at'):state['first_write_at']=now();persist()
 return gog(*args)
def folder(path):
 if path in ['', '.']:return ROOT
 if path in state['folders']:return state['folders'][path]
 parent=folder(str(pathlib.PurePosixPath(path).parent));name=pathlib.PurePosixPath(path).name
 d=gog('ls','--parent',parent,'--max','100');assert not d.get('nextPageToken')
 matches=[x for x in d['files'] if x['name']==name];assert not matches,'Existing destination requires recovery review: '+path
 r=mutate('mkdir',name,'--parent',parent);fid=r['folder']['id'];state['folders'][path]=fid;persist();m=get(fid);assert m['parents']==[parent] and m['name']==name and m['driveId']==DRIVE;assert sig(gog('permissions',fid))==sig(rp);return fid
def openfile(out):
 if out.suffix in ['.docx','.xlsx']:
  with zipfile.ZipFile(out) as z:
   for n in z.namelist():
    if n=='word/document.xml' or n.startswith('xl/worksheets/') and n.endswith('.xml'):ET.fromstring(z.read(n))
  return 'Own downloaded Office document XML parsed'
 if out.suffix=='.pdf':
  from pypdf import PdfReader
  r=PdfReader(out);assert len(r.pages)>0;return 'Own downloaded PDF pages opened'
 if out.suffix=='.zip':
  with zipfile.ZipFile(out) as z:assert z.testzip() is None
  return 'Own downloaded plugin ZIP integrity opened'
 from PIL import Image
 im=Image.open(out);im.load();return 'Own downloaded image decoded'
_destination_names = {}
def destination_names(parent):
 if parent not in _destination_names:
  names=set();token=None
  while True:
   args=['ls','--parent',parent,'--max','100']
   if token:args += ['--page',token]
   listing=gog(*args);names.update(x['name'] for x in listing['files']);token=listing.get('nextPageToken')
   if not token:break
  _destination_names[parent]=names
 return _destination_names[parent]
def copyrow(r):
 fid=r['source_id']
 if fid in state['copies']:return state['copies'][fid]
 assert r.get('active_copy_source_id',fid)==fid, 'Duplicate alias requires existing canonical proof, not another copy'
 sf=POOL.submit(get,fid);pf=POOL.submit(gog,'permissions',fid);source=sf.result();s=orig[fid];assert all(source.get(k)==s.get(k) for k in ['md5Checksum','size','modifiedTime','parents'])
 assert source.get('md5Checksum') or source.get('mimeType')=='application/vnd.google-apps.document', 'Unsupported native type: hold before copying'
 perms=pf.result();assert sig(perms)==sig(rp),'Source access differs; hold affected item'
 parent=folder(str(pathlib.PurePosixPath(r['planned_path']).parent));name=pathlib.PurePosixPath(r['planned_path']).name
 if fid in state['pending']:did=state['pending'][fid]
 else:
  assert name not in destination_names(parent), 'Destination collision: reconcile first'
  result=mutate('copy',fid,name,'--parent',parent);did=result['file']['id'];_destination_names.setdefault(parent,set()).add(name);state['pending'][fid]=did;persist()
 from folder_output_verification import verify_output
 dest=get(did)
 assert dest['parents']==[parent] and dest['name']==name and dest['driveId']==DRIVE
 assert sig(gog('permissions',did))==sig(perms)
 method,local_path=verify_output(P,r,source,dest,gog)
 latest=get(fid);assert all(latest.get(k)==source.get(k) for k in ['md5Checksum','size','modifiedTime','parents']), 'Source changed during copy'
 proof={'source_id':fid,'active_id':did,'name':name,'path':r['planned_path'],'local_path':local_path,'md5Checksum':source.get('md5Checksum'),'size':source.get('size'),'verified_at':now(),'permissions_matched':True,'content_read':method}
 save(fid+'-copy-proof.json',proof);state['copies'][fid]=proof;state['pending'].pop(fid,None);persist();return proof
def archive(fid,parent):
 if fid in state['archived']:return
 if fid not in state['copies']:
  row=next(r for r in plan['file_plan'] if r['source_id']==fid)
  cid=row.get('active_copy_source_id',fid)
  if cid!=fid and cid in state['copies']:
   from edith_duplicate_proof import make_proof
   canonical=state['copies'][cid];source=get(fid);active=get(canonical['active_id'])
   expected=state['folders'][str(pathlib.PurePosixPath(row['planned_path']).parent)]
   assert active.get('parents')==[expected] and active.get('driveId')==DRIVE
   proof=make_proof(row,orig[fid],source,active,canonical,sig(gog('permissions',fid)),sig(gog('permissions',active['id'])),now())
   save(fid+'-copy-proof.json',proof);state['copies'][fid]=proof;persist()
 current=get(fid)
 proof=state['copies'].get(fid,{})
 assert proof.get('active_id') and all(current.get(k)==proof.get(k) for k in ('md5Checksum','size')), 'Source changed before archive; retain in place'
 if current['parents']!=[parent]:mutate('move',fid,'--parent',parent)
 m=get(fid);assert m['parents']==[parent]
 for k in ['md5Checksum','size']:assert m.get(k)==current.get(k)
 state['archived'].append(fid);persist()

if __name__=='__main__':
 review=json.loads((P/'plan-review.json').read_text())
 root=get(ROOT);assert root['driveId']==DRIVE and not root.get('trashed');assert root['capabilities'].get('canAddChildren')
 rows={r['source_id']:r for r in plan['file_plan']}
 for fid in review['pilot_source_ids']:
  proof=copyrow(rows[fid]);print('Verified pilot copy',fid,proof['active_id'],flush=True)
 print('Pilot copies verified; content self-review and archive pending.',flush=True)

