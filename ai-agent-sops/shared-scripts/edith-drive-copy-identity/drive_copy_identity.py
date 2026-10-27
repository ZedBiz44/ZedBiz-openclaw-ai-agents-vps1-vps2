"""Persist a Google-reserved destination ID before a binary copy can begin.

Google documents that repeated files.copy calls using the same pre-generated
ID cannot create duplicate files. Native Workspace copies are excluded.
"""
import hashlib,json,time
from pathlib import Path

FIELDS='id,name,mimeType,parents,driveId,md5Checksum,size,modifiedTime,trashed'
FOLDER='application/vnd.google-apps.folder'

def path_for(base,args):
    return Path(base)/'copy-identities'/(hashlib.sha256(json.dumps(list(args)).encode()).hexdigest()+'.json')

def has_identity(base,args):
    p=path_for(base,args)
    if not p.exists():return False
    d=json.loads(p.read_text())
    return d.get('version')==1 and d.get('args')==list(args) and bool(d.get('destination_id'))

def destination_drive(record):
    destination=record.get('destination')
    return record['source'].get('driveId') if destination is None else destination.get('driveId')

def verify(record,item):
    args=record['args'];source=record['source']
    if item.get('id')!=record['destination_id'] or item.get('name')!=args[2] or item.get('parents')!=[args[-1]] or item.get('trashed'):
        raise ValueError('Reserved destination identity or placement mismatch')
    if any(str(item.get(k))!=str(source.get(k)) for k in ['md5Checksum','size','mimeType']):
        raise ValueError('Reserved destination content mismatch')
    if str(item.get('driveId'))!=str(destination_drive(record)):
        raise ValueError('Reserved destination drive mismatch')
    return {'file':item,'reserved_destination_id':record['destination_id']}

def approved_parent(raw,args):
    parent=raw('get',args[-1],'--fields',FIELDS)['file']
    if parent.get('id')!=args[-1] or parent.get('mimeType')!=FOLDER or parent.get('trashed'):
        raise ValueError('Approved destination parent mismatch')
    return parent

def verify_authority(record,parent):
    destination=record.get('destination')
    if destination is None:
        if parent.get('driveId')!=record['source'].get('driveId'):
            raise ValueError('Legacy copy identity cannot adopt a cross-drive destination')
    elif any(parent.get(k)!=destination.get(k) for k in ['id','mimeType','driveId','trashed']):
        raise ValueError('Approved destination authority changed')

def execute(base,args,raw,sleep=time.sleep):
    from execution_guard import save
    args=list(args)
    if len(args)!=5 or args[0]!='copy' or args[3]!='--parent':raise ValueError('Unexpected copy scope')
    source=raw('get',args[1],'--fields',FIELDS)['file']
    if source.get('mimeType','').startswith('application/vnd.google-apps.'):
        return raw(*args) # Native files cannot use pre-generated IDs.
    if not source.get('md5Checksum') or source.get('size') is None or source.get('trashed'):
        raise ValueError('Binary source integrity cannot be established')
    parent=approved_parent(raw,args)
    p=path_for(base,args);p.parent.mkdir(mode=0o700,exist_ok=True)
    existing=p.exists()
    if existing:
        record=json.loads(p.read_text())
        if not has_identity(base,args):raise ValueError('Invalid existing copy identity')
        if any(source.get(k)!=record['source'].get(k) for k in ['md5Checksum','size','mimeType','driveId','modifiedTime','parents']):
            raise ValueError('Source changed after destination identity reservation')
        verify_authority(record,parent)
    else:
        reserved=raw('generate-id')['id']
        if not isinstance(reserved,str) or not reserved.strip():raise ValueError('Missing generated ID')
        record={'version':1,'args':args,'destination_id':reserved,'source':source,
                'destination':{k:parent.get(k) for k in ['id','mimeType','driveId','trashed']},'attempts':0}
        save(p,record) # Durable before the first mutating request.

    def lookup():
        try:item=raw('get',record['destination_id'],'--fields',FIELDS)['file']
        except RuntimeError as e:
            if '404' in str(e) or 'notFound' in str(e) or 'File not found' in str(e):return None
            raise
        return verify(record,item)

    if existing:
        found=lookup()
        if found:return found
    last_error=None
    for attempt in range(2):
        record['attempts']+=1;save(p,record)
        try:
            result=raw(*args[:3],'--destination-id',record['destination_id'],*args[3:])
            if result.get('file',{}).get('id')!=record['destination_id']:
                raise ValueError('Copy did not honor the reserved ID')
        except RuntimeError as e:
            last_error=e
            if not any(s in str(e).lower() for s in ['timeout','timed out','connection reset','unexpected eof','500','502','503','504','409','conflict']):raise
        found=lookup()
        if found:
            record['confirmed']=True;save(p,record);return found
        if attempt==0:sleep(3)
    raise RuntimeError('Reserved copy remains unresolved; retain the same destination ID, do not generate another') from last_error
