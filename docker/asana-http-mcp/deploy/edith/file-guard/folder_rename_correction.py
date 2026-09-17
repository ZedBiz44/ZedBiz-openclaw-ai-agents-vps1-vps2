"""One explicitly approved folder-name correction; not general rename authority."""
import fcntl
from pathlib import Path
from datetime import datetime, timezone
from execution_guard import read, save
ROOT='1H4Eu423jUNS4fbtynAmsPxqSmQ2TpUgU'
FOLDER='135v4VgqqlqsgsnTUq-LaSvpE4Oyw6i54'
CHILD='1PobhHFSjRtCkiW3FjHENlxpQhulN8Qo0'
DRIVE='0ACpgWCt49vmJUk9PVA'
OLD='Research'
NEW='ZVIM-Comparisons-Research'
FIELDS='id,name,mimeType,parents,driveId,modifiedTime,trashed'
def validate(root,args,folder,child):
 if root!=ROOT or tuple(args)!=('rename',FOLDER,NEW):raise ValueError('Only the approved Research-folder rename is allowed')
 if folder.get('id')!=FOLDER or folder.get('mimeType')!='application/vnd.google-apps.folder' or folder.get('parents')!=[ROOT] or folder.get('driveId')!=DRIVE or folder.get('trashed'):raise ValueError('Folder identity or location changed')
 if folder.get('name') not in (OLD,NEW):raise ValueError('Unexpected current folder name')
 if child.get('id')!=CHILD or child.get('parents')!=[FOLDER] or child.get('driveId')!=DRIVE or child.get('trashed'):raise ValueError('Protected Whiteboard identity or parent changed')
def rename(base,root,args,call):
 if root!=ROOT or tuple(args)!=('rename',FOLDER,NEW):raise ValueError('Only the approved Research-folder rename is allowed')
 base=Path(base)
 with (base/'mutation.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  folder=call('get',FOLDER,'--fields',FIELDS)['file']
  child=call('get',CHILD,'--fields',FIELDS)['file']
  validate(root,args,folder,child)
  path=base/'approved-research-rename.json'
  prior=read(path) if path.exists() else None
  if prior and child!=prior['protected_before']:raise ValueError('Protected folder metadata changed; reconcile before proceeding')
  if folder['name']==NEW:
   result={'status':'verified-existing','file':folder,'protected_unchanged':True}
   if prior:
    prior.update(status='confirmed',result=result);save(path,prior)
   return result
  if prior:raise RuntimeError('Prior rename attempt requires reconciliation; do not repeat automatically')
  listing=call('ls','--parent',ROOT,'--max','100')
  if listing.get('nextPageToken'):raise ValueError('Parent listing incomplete')
  if any(x.get('name')==NEW and x.get('id')!=FOLDER for x in listing.get('files',[])):raise ValueError('Destination name already exists')
  record={'status':'intent','folder_before':folder,'protected_before':child,'args':list(args),'authorized_correction_task':'1218615345268193','review_approval':'1218559622039883','started':datetime.now(timezone.utc).isoformat()}
  save(path,record)
  try:
   call(*args)
   after=call('get',FOLDER,'--fields',FIELDS)['file']
   child_after=call('get',CHILD,'--fields',FIELDS)['file']
   validate(root,args,after,child_after)
   if after['name']!=NEW or child_after!=child:raise ValueError('Rename or protected-folder readback failed')
   result={'status':'renamed-and-verified','file':after,'protected_unchanged':True}
   record.update(status='confirmed',result=result);save(path,record);return result
  except BaseException:
   record['status']='uncertain';save(path,record);raise
