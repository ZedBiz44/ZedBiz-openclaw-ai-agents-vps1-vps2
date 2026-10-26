"""Download checksum-pinned assets into the build context; extract only named binaries."""
import hashlib,io,json,os,pathlib,tarfile,urllib.request,zipfile
root=pathlib.Path(__file__).resolve().parent
assets=root/'tool-assets';assets.mkdir(exist_ok=True)
receipt=[]
for spec in json.loads((root/'tool-assets.json').read_text()):
 req=urllib.request.Request(spec['url'],headers={'User-Agent':'ZedBiz-release-audit'})
 with urllib.request.urlopen(req,timeout=60) as r:data=r.read()
 assert hashlib.sha256(data).hexdigest()==spec['sha256'],'Asset digest mismatch: '+spec['tool']
 for name in spec['members']:
  if spec.get('raw'):binary=data
  elif spec['url'].endswith('.zip'):
   with zipfile.ZipFile(io.BytesIO(data)) as z:
    matches=[m for m in z.infolist() if pathlib.PurePosixPath(m.filename).name==name and not m.is_dir()]
    assert len(matches)==1;binary=z.read(matches[0])
  else:
   with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
    matches=[m for m in t if pathlib.PurePosixPath(m.name).name==name and m.isfile()]
    assert len(matches)==1;binary=t.extractfile(matches[0]).read()
  assert binary.startswith(b'\x7fELF'),'Expected Linux executable: '+name
  dest=assets/name;dest.write_bytes(binary);dest.chmod(0o755)
  receipt.append({'binary':name,'version':spec['version'],'assetSha256':spec['sha256'],'binarySha256':hashlib.sha256(binary).hexdigest()})
(root/'tool-assets-proof.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
