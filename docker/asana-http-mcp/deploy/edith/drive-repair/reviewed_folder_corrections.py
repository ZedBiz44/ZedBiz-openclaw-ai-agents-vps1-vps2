"""Exact reviewer-approved folder corrections; no general move/rename authority."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl, json

DRIVE='0ACpgWCt49vmJUk9PVA'
LAUGHS='1u-Px3AK0aYrtcUmepbqorMIHtDR0tN3-'
ARCHIVE='1e2ROmD5TW8qQbTlVNk2NFSednxybttko'
INCANMORE='166AkHunzLAWRw3jPC-8PfYS74I0A6EAc'
MOVES=dict(zip(['1EnFE7g2GJ1eEM8X1jlGSl5Bx8d46iUG-','1AB25Q0FtajuIYewABhrB9un6MeBu19Il','1NZnBZD3B7UkEJwrELBMhVg6ICwebSUDP','1ET-hA-jnB1e4K3HAeZVUV9SGW1uKCYVs','1aAIWI9MAl0F77ySUOKYkhHLnxDaz8TWj','1CsKCc2lZxHfSHBFdRMXgyK_pb5q29Jv3','19fPUZcwe8V0JO_pLkZGhiRMlTuzXDm5L'],['Research','Website-Content','Social-Media-Graphics','Source-Files','Brand','Videos','Graphics']))
RENAMES={
 '1DD59dvX3vUAEYk7p67HE6zJDRgRk23y4':('InCanmore-Reference-Graphics','ZVIM-InCanmore-Reference-Graphics'),
 '1e3Wr61pk-DqDOD8y_3vFCnk9M-91-66S':('InCanmore-Photos','ZVIM-InCanmore-Photos'),
 '1GZ1myBdgZtoM13P1tMwi8jbx5sztw6Ln':('InCanmore-Graphics','ZVIM-InCanmore-Website-Graphics'),
 '1G2r991DHH3SUeeNIHfyro1iYvFdyMsQh':('InCanmore-Content','ZVIM-InCanmore-Website-Content'),
 '12T8i2aaZZW5cyJINZ6LhxQoof8gMJ3Fv':('InCanmore-Logos','ZVIM-InCanmore-Logos')}
FIELDS='id,name,mimeType,parents,driveId,trashed,modifiedTime'
def supports(root,args):
 return (root==LAUGHS and len(args)==4 and args[0]=='move' and args[1] in MOVES and args[2:] == ('--parent',ARCHIVE)) or (root==INCANMORE and len(args)==3 and args[0]=='rename' and args[1] in RENAMES and args[2]==RENAMES[args[1]][1])
def folder(meta):
 if meta.get('mimeType')!='application/vnd.google-apps.folder' or meta.get('driveId')!=DRIVE or meta.get('trashed'):raise ValueError('Unexpected folder identity, Drive or trash state')
def children(call,parent):
 result=[];token=None;seen=set()
 while True:
  args=['ls','--parent',parent,'--max','100','--fields','files('+FIELDS+'),nextPageToken']
  if token:args+=['--page',token]
  d=call(*args)
  if 'files' not in d:raise ValueError('Missing folder listing')
  for item in d['files'] or []:
   if item.get('parents')!=[parent] or item.get('driveId')!=DRIVE:raise ValueError('Unexpected listed parent or Drive')
   result.append(item)
  token=d.get('nextPageToken')
  if not token:return result
  if token in seen:raise ValueError('Repeated page token')
  seen.add(token)
def apply(base,root,args,call):
 args=tuple(args)
 if not supports(root,args):raise ValueError('Outside the exact reviewer-approved corrections')
 base=Path(base);fid=args[1]
 def get(i):
  m=call('get',i,'--fields',FIELDS)['file']
  if m.get('id')!=i:raise ValueError('Wrong returned ID')
  folder(m);return m
 def save(record):
  tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(record,indent=2));tmp.replace(path)
 with (base/'mutation.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  get(root);before=get(fid);path=base/('reviewed-folder-correction-'+fid+'.json')
  prior=json.loads(path.read_text()) if path.exists() else None
  if args[0]=='move':
   dest=get(ARCHIVE)
   if dest['parents']!=[root] or before.get('name')!=MOVES[fid] or before.get('parents') not in ([root],[ARCHIVE]):raise ValueError('Archive boundary or source changed')
   target_parent=ARCHIVE;target_name=MOVES[fid]
   # These are leftover containers after every original file was retained.
   queue=[fid];seen=set()
   while queue:
    current=queue.pop()
    if current in seen:raise ValueError('Folder cycle')
    seen.add(current)
    for item in children(call,current):folder(item);queue.append(item['id'])
  else:
   if before.get('name') not in RENAMES[fid] or len(before.get('parents',[]))!=1:raise ValueError('Unexpected rename source')
   parent=get(before['parents'][0])
   if parent.get('parents')!=[root]:raise ValueError('Rename is not inside the approved second level')
   target_parent=parent['id'];target_name=RENAMES[fid][1]
  if prior and (prior['root']!=root or prior['args']!=list(args)):raise ValueError('Journal scope mismatch')
  if before['name']==target_name and before['parents']==[target_parent]:
   result={'status':'verified-existing','file':before}
   if prior:prior.update(status='confirmed',result=result);save(prior)
   return result
  if prior:raise RuntimeError('Previous attempted write has not reached its exact result; reconcile, never blindly retry')
  if any(x['name']==target_name and x['id']!=fid for x in children(call,target_parent)):raise ValueError('Destination name collision')
  record={'status':'intent','root':root,'args':list(args),'before':before,'started':datetime.now(timezone.utc).isoformat(),'authority':'Jack authorized Ruby corrections; exact Asana review IDs 1218574348329943 and 1218559452275700'}
  save(record)
  try:
   call(*args);after=get(fid)
   if after['name']!=target_name or after['parents']!=[target_parent]:raise ValueError('Correction readback failed')
   record.update(status='confirmed',result={'status':'corrected-and-verified','file':after});save(record);return record['result']
  except BaseException:
   record['status']='uncertain';save(record);raise

