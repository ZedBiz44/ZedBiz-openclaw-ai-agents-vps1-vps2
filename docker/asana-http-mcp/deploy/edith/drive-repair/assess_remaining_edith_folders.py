from pathlib import Path
import importlib.util,json,os,sys
os.umask(0o077)
p=Path('/home/node/.openclaw');base=p/'private/folder-cleanup';sys.path.insert(0,str(p/'workspace/scripts'))
from edith_folder_work_summary import assess
spec=importlib.util.spec_from_file_location('work',base/'albertawide/work.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
rows=json.loads("[{\"task\":\"1218559788686767\",\"name\":\"Organize and verify — ZVIM-LightningIM\",\"root\":\"1JBXsbZukxYOdEhy-kBxurKg_KvNKdVyT\",\"approval\":\"1218559789137828\",\"slug\":\"lightningim\"},{\"task\":\"1218559621792077\",\"name\":\"Organize and verify — ZVIM-Paradise-Fishing\",\"root\":\"1TePQyv4t2tgFs23CVkw5S3w4hvf1CX91\",\"approval\":\"1218559452593223\",\"slug\":\"paradise-fishing\"},{\"task\":\"1218559536949282\",\"name\":\"Organize and verify — ZVIM-FKLass\",\"root\":\"1e8yB0pBq2g8LnRMQunkh8if2Y7FS9-C1\",\"approval\":\"1218559622201055\",\"slug\":\"fklass\"},{\"task\":\"1218559788863817\",\"name\":\"Organize and verify — ZVIM-4-Day-Build-A-Business\",\"root\":\"1BEd21EgCO9UoJ3Hisof901Bfh6qZ98Oz\",\"approval\":\"1218559452895543\",\"slug\":\"4-day-build-a-business\"},{\"task\":\"1218559621676002\",\"name\":\"Organize and verify — ZVIM-Passion-Profits-Project\",\"root\":\"1H4V7PyZcP352lKz3N2NLUAwMF6HS-jzm\",\"approval\":\"1218559622386305\",\"slug\":\"passion-profits-project\"},{\"task\":\"1218559788958539\",\"name\":\"Organize and verify — ZVIM-Lifestyle-Business-Mindset\",\"root\":\"1ltxAX2grAGJiOcgu_AFvygUHY-s91wnw\",\"approval\":\"1218559789594246\",\"slug\":\"lifestyle-business-mindset\"}]")
template=json.loads((base/'laughs-and-fun/registry.json').read_text())
summary=[]
for row in rows:
 w.P=base/row['slug'];w.P.mkdir(mode=0o700,exist_ok=True);(w.P/'cache').mkdir(mode=0o700,exist_ok=True);w.ROOT=row['root']
 root=w.get(row['root']);assert root['name']==row['name'].split(' — ')[1] and root['driveId']==w.DRIVE and not root.get('trashed')
 chain=[root];seen={root['id']}
 while chain[-1]['id']!=w.DRIVE:
  parents=chain[-1].get('parents',[]);assert len(parents)==1
  parent=parents[0];assert parent not in seen;seen.add(parent);chain.append(w.get(parent))
 assert any(x['id']=='13gnUFLQotLx3SKaZfrXh0L3UXU6dGA-n' for x in chain)
 rp=w.P/'registry.json'
 if not rp.exists():
  registry=json.loads(json.dumps(template));client=next(iter(registry['clients'].values()));client.update(client_root_folder_id=row['root'],archive_folder_id=None,template_ids={});registry['clients']={row['slug']:client};registry['runtime'].update(receipt_log=str(w.P/'receipts.jsonl'),cache_dir=str(w.P/'cache'));rp.write_text(json.dumps(registry,indent=2));rp.chmod(0o600)
 w.save('ancestry.json',chain[::-1])
 inv=w.inventory();name='initial-inventory.json' if not (w.P/'initial-inventory.json').exists() else 'preflight-inventory-current.json';w.save(name,inv)
 assessment=assess(inv);w.save('workload-assessment.json',assessment)
 result={'task':row['task'],'slug':row['slug'],'items':len(inv['items']),'files':sum(v['files'] for v in assessment['groups'].values()),'groups':assessment['groups']}
 summary.append(result);print(json.dumps(result),flush=True)
(base/'remaining-six-workload-assessment.json').write_text(json.dumps(summary,indent=2))


