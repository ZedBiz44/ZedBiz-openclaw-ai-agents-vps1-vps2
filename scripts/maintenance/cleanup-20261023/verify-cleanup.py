"""Read-only acceptance plus a small private/sanitized receipt for this cleanup."""
import hashlib,json,pathlib,shutil,subprocess,time,urllib.request
ROOT=pathlib.Path('/opt/openclaw/backups/cleanup-20261023')
baseline=json.loads((ROOT/'baseline.json').read_text())
agents=[]
for before in baseline:
 a=before['agent'];d=json.loads(subprocess.check_output(['docker','inspect',a]))[0]
 changed=[f for f,h in before['files'].items() if hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()!=h]
 with urllib.request.urlopen('https://'+a+'.zbiz.ca/healthz',timeout=20) as r:status=r.status
 manifest=pathlib.Path('/opt/openclaw/recovery')/(a+'-20261018')/'manifest.json'
 if not manifest.exists():manifest=pathlib.Path('/opt/openclaw/recovery/fleet-20261018')/a/'manifest.json'
 m=json.loads(manifest.read_text())
 identities=all(json.loads(subprocess.check_output(['docker','image','inspect',im['ref']]))[0]['Id']==im['id'] for im in m['images'])
 wrapper=hashlib.sha256(pathlib.Path(m['wrapper']).read_bytes()).hexdigest()==m['wrapper_sha256']
 row={'agent':a,'health':d['State']['Health']['Status'],'restarts':d['RestartCount'],'oomKilled':d['State']['OOMKilled'],
      'sameImage':d['Image']==before['image'],'publicHealth':status,'currentFilesChanged':changed,
      'recoveryImagesMatch':identities,'recoveryArchiveExists':pathlib.Path(m['archive']).is_file(),'wrapperHashMatches':wrapper}
 agents.append(row)
 assert row['health']=='healthy' and row['restarts']==before['restarts'] and not row['oomKilled'] and row['sameImage']
 assert status==200 and not changed and identities and wrapper and row['recoveryArchiveExists']
archives=[]
for p in ROOT.glob('*-archive.json'):
 d=json.loads(p.read_text())
 assert d['status']=='complete' and d['originalSHA256']==d['decompressedSHA256']
 assert not pathlib.Path(d['original']).exists() and pathlib.Path(d['archive']).stat().st_size==d['compressedBytes']
 archives.append({k:d[k] for k in ['original','archive','originalBytes','compressedBytes','originalSHA256','decompressedSHA256','compressedSHA256','tarEntries','reclaimedBytes']})
loose=[]
for p in (ROOT/'loose-files').glob('*.json'):
 d=json.loads(p.read_text());assert d['status']=='complete'
 assert hashlib.sha256(pathlib.Path(d['archive']).read_bytes()).hexdigest()==d['archiveSHA256']
 assert all(not pathlib.Path(r['path']).exists() for r in d['files'])
 loose.append({'agent':d['agent'],'count':len(d['files']),'originalBytes':sum(r['size'] for r in d['files']),'archiveBytes':pathlib.Path(d['archive']).stat().st_size})
rehearsals=[]
for p in (ROOT/'rehearsals').glob('*.json'):
 d=json.loads(p.read_text());assert d['status']=='complete' and not pathlib.Path(d['source']).exists()
 rehearsals.append({'source':d['source'],'archive':d['archive'],'archiveSHA256':d['archiveSHA256'],'entries':len(d['entries']),
                    'regularFileBytes':sum(r['size'] for r in d['entries'].values() if r['type']=='file'),'archiveBytes':pathlib.Path(d['archive']).stat().st_size})
disk=shutil.disk_usage('/')
assert len(agents)==11 and len(archives)==22 and len(loose)==11 and len(rehearsals)==2
assert sum(r['count'] for r in loose)==783
result={'verifiedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'agents':agents,'archives':archives,'looseFiles':loose,'rehearsals':rehearsals,
        'historicalArchiveCount':len(archives),'archiveBytesReclaimed':sum(r['reclaimedBytes'] for r in archives),
        'looseFileCount':sum(r['count'] for r in loose),'diskTotalBytes':disk.total,'diskFreeBytes':disk.free}
(ROOT/'final-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)

