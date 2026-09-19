"""Archive planned, emptied original containers after verified file retention."""
from pathlib import Path
from reviewed_folder_corrections import children, folder, FIELDS

def validate_plan(plan,before,review,state,root,args,protected):
 fid=args[1];originals={x['id']:x for x in before['items']}
 source=originals.get(fid,{})
 if source.get('mimeType')!='application/vnd.google-apps.folder' or source.get('parents')!=[root]:raise ValueError('Only original first-level containers can be archived')
 proposed=[x for x in plan.get('folder_archive_plan',[]) if x.get('source_id')==fid]
 if len(proposed)!=1:raise ValueError('Container archive is not in the reviewed saved plan')
 row=proposed[0];target=row.get('archive_path')
 if not target or target not in review.get('archive_paths',[]) or state.get('folders',{}).get(target)!=args[3]:raise ValueError('Container archive destination not verified')
 if row.get('source_name')!=source.get('name'):raise ValueError('Container name differs from reviewed original')
 descendant={fid}
 while True:
  more=descendant|{i for i,x in originals.items() if descendant.intersection(x.get('parents',[]))}
  if more==descendant:break
  descendant=more
 if descendant.intersection(protected):raise ValueError('Protected item exists inside original container')
 active_ids={x.get('active_id') for x in state.get('copies',{}).values()}
 if descendant.intersection(active_ids):raise ValueError('An active output is inside the source container')
 rows={x['source_id']:x for x in plan['file_plan']}
 for i in descendant:
  x=originals[i]
  if x.get('mimeType')=='application/vnd.google-apps.folder':continue
  proof=state.get('copies',{}).get(i,{})
  if rows.get(i,{}).get('action')!='copy' or i not in state.get('archived',[]) or not proof.get('active_id') or not proof.get('permissions_matched') or not proof.get('content_read'):raise ValueError('Original file retention is unfinished')
  if any(x.get(k)!=proof.get(k) for k in ['md5Checksum','size']):raise ValueError('Original file proof differs')

def execute(base,root,args,call):
 import json
 base=Path(base);before=json.loads((base/'initial-inventory.json').read_text());originals={x['id']:x for x in before['items']}
 fid=args[1];target=args[3]
 def get(i):
  result=call('get',i,'--fields',FIELDS)['file'];folder(result)
  if result.get('id')!=i:raise ValueError('Wrong returned folder ID')
  return result
 source=get(fid);dest=get(target);get(root)
 if dest.get('parents')!=[root]:raise ValueError('Archive container must be inside this exact project root')
 if source['name']!=originals[fid]['name'] or source['parents'] not in ([root],[target]):raise ValueError('Original folder changed')
 if source['parents']==[target]:return {'file':source,'reconciled':True}
 queue=[fid];seen=set()
 while queue:
  i=queue.pop()
  if i in seen:raise ValueError('Folder cycle')
  seen.add(i)
  for x in children(call,i):
   folder(x)
   if x['id'] not in originals or originals[x['id']].get('parents')!=x['parents'] or originals[x['id']].get('name')!=x['name']:raise ValueError('Unexpected contents in retained container')
   queue.append(x['id'])
 if any(x['name']==source['name'] and x['id']!=fid for x in children(call,target)):raise ValueError('Archive name collision')
 call(*args);after=get(fid)
 if after['parents']!=[target] or after['name']!=source['name']:raise ValueError('Archive readback failed')
 return {'file':after,'verified_empty_original_container':True}

