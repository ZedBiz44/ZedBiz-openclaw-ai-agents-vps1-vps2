"""Confirm persisted guard rejects old images and corrupted acquisition code."""
import ast,json,pathlib,subprocess,sys
P=pathlib.Path;ROOT=P(__file__).resolve().parent;new,old=sys.argv[1:]
tree=ast.parse((ROOT/'deploy.py').read_text());guard=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GUARD' for t in n.targets))
def run(image,mount=None):
 args=['docker','run','--rm','--network','none','--entrypoint','sh']
 if mount:args+=['-v',mount]
 return subprocess.run(args+[image,'-c',guard],capture_output=True,text=True,timeout=45)
assert run(new).returncode==0
assert run(old).returncode!=0
corrupt=ROOT/'corrupt-acquire.py';corrupt.write_text('raise SystemExit("test-only missing implementation")\n')
assert run(new,str(corrupt)+':/opt/zedbiz/wiki-lock/acquire-lock.py:ro').returncode!=0
proof={'passed':True,'newImageAccepted':True,'oldImageRejected':True,'tamperedAcquisitionCodeRejected':True}
(ROOT/'gate-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
