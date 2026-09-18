"""List legacy ZIPs and selectively extract useful documents; never run contents."""
import argparse,hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath
DOCS={'.pdf','.doc','.docx','.odt','.rtf','.txt','.md','.csv','.xls','.xlsx','.ods','.ppt','.pptx','.odp','.epub'}
MAX_ARCHIVE=512*1024*1024
MAX_MEMBER=100*1024*1024
MAX_MEMBERS=10000
def safe_member(item):
 p=PurePosixPath(item.filename)
 return (not p.is_absolute() and '..' not in p.parts and '\\' not in item.filename
         and ':' not in item.filename and not stat.S_ISLNK(item.external_attr>>16))
def triage(source,destination,members=()):
 source=Path(source);dest=Path(destination)
 if source.stat().st_size>MAX_ARCHIVE:return {'status':'deferred-too-large','reason':'Archive exceeds512MiB; preserved without extraction'}
 try:
  with zipfile.ZipFile(source) as z:
   items=z.infolist()
   if len(items)>MAX_MEMBERS:return {'status':'deferred-too-large','reason':'More than10000 members'}
   if len({x.filename for x in items})!=len(items):return {'status':'deferred-unsupported','reason':'Duplicate member paths'}
   docs=[x.filename for x in items if not x.is_dir() and PurePosixPath(x.filename).suffix.lower() in DOCS]
   result={'status':'listed','member_count':len(items),'useful_documents':docs,'extracted':[]}
   byname={x.filename:x for x in items}
   for name in members:
    item=byname.get(name)
    if not item or name not in docs:raise ValueError('Only listed useful documents may be extracted')
    if not safe_member(item):raise ValueError('Unsafe archive member path or symlink')
    if item.flag_bits&1:return {'status':'deferred-encrypted','reason':'Selected document is encrypted','useful_documents':docs,'extracted':result['extracted']}
    if item.file_size>MAX_MEMBER or item.file_size>max(item.compress_size,1)*200:
     return {'status':'deferred-too-large','reason':'Selected document exceeds extraction limit','useful_documents':docs,'extracted':result['extracted']}
    target=dest.joinpath(*PurePosixPath(name).parts)
    dest.mkdir(parents=True,exist_ok=True)
    if not target.resolve().is_relative_to(dest.resolve()):raise ValueError('Extraction destination escapes staging folder')
    target.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation refuses overwrite; partial outputs remain explicit on failure.
    md5=hashlib.md5();total=0
    with z.open(item) as r,target.open('xb') as w:
     while True:
      chunk=r.read(1024*1024)
      if not chunk:break
      total+=len(chunk)
      if total>MAX_MEMBER or total>item.file_size:raise ValueError('Expanded data exceeds declared size')
      w.write(chunk);md5.update(chunk)
    result['extracted'].append({'member':name,'path':str(target),'size':total,'md5Checksum':md5.hexdigest()})
   return result
 except (zipfile.BadZipFile,NotImplementedError) as e:
  return {'status':'deferred-unsupported','reason':type(e).__name__}
def main():
 p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('staging');p.add_argument('--extract',action='append',default=[]);a=p.parse_args()
 allowed=Path('/home/node/.openclaw/private/folder-cleanup').resolve()
 if not Path(a.staging).resolve().is_relative_to(allowed):raise ValueError('Use the approved private folder-cleanup staging area')
 print(json.dumps(triage(a.archive,a.staging,a.extract),indent=2))
if __name__=='__main__':main()
