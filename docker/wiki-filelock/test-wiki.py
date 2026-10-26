"""Exercise actual packaged ingest/compile/lint code against only a synthetic vault."""
import json,pathlib,subprocess,sys,time
P=pathlib.Path;ROOT=P(__file__).resolve().parent;image=sys.argv[1]
vault=ROOT/('synthetic-wiki-'+str(int(time.time())));vault.mkdir();vault.chmod(0o777)
# Root test directory must permit the node user to create synthetic import inputs.
args=['docker','run','--rm','--network','none','-v',str(ROOT)+':/fixture','--entrypoint','node',image,'/fixture/wiki-worker.mjs','/fixture/'+vault.name]
p=subprocess.run(args+['seed'],capture_output=True,text=True,timeout=90);assert p.returncode==0,p.stderr
jobs=[subprocess.Popen(args+[str(i)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for i in range(3)]
rounds=[]
for job in jobs:
 out,err=job.communicate(timeout=180);assert job.returncode==0,err
 rounds += [json.loads(s) for s in out.splitlines() if s.startswith('{')]
assert len(rounds)==9 and len({r['ingested'] for r in rounds})==9
for row in rounds:
 p=vault/row['ingested'];assert p.is_file(),str(p)
proof={'passed':True,'containers':3,'ingestCompileLintRounds':9,'allNineSourcePagesRetained':True,'rounds':rounds}
(ROOT/'wiki-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
