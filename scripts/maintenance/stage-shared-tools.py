import urllib.request,json,pathlib,tarfile,hashlib,os
dest=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003/tools-stage');dest.mkdir(exist_ok=True)
jobs=[('openclaw/gogcli','v0.43.0','gogcli_0.43.0_linux_amd64.tar.gz','gog','gog-real'),('pimalaya/himalaya','v2.2.1','himalaya.x86_64-linux.tgz','himalaya','himalaya'),('BurntSushi/ripgrep','15.2.0','ripgrep-15.2.0-x86_64-unknown-linux-musl.tar.gz','rg','rg'),('jqlang/jq','jq-1.8.2','jq-linux-amd64',None,'jq')]
def fetch(u):return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'ZedBiz-maintenance'}),timeout=60).read()
for repo,tag,asset,binary,target in jobs:
 d=json.loads(fetch('https://api.github.com/repos/'+repo+'/releases/tags/'+tag));a=next(x for x in d['assets'] if x['name']==asset);b=fetch(a['browser_download_url']);digest='sha256:'+hashlib.sha256(b).hexdigest()
 if a.get('digest') and a['digest']!=digest:raise RuntimeError('Digest mismatch '+asset)
 p=dest/asset;p.write_bytes(b)
 if binary:
  with tarfile.open(p) as t:
   m=next(m for m in t.getmembers() if m.isfile() and pathlib.PurePosixPath(m.name).name==binary);(dest/target).write_bytes(t.extractfile(m).read())
 else:(dest/target).write_bytes(b)
 os.chmod(dest/target,0o755)
 print(target,tag,digest,flush=True)
