import sys
sys.argv=['reboot-ready','audit']
exec(open('/root/cody-vps2-followup-20261023/followup.py').read().split("if action==")[0])
for n in ['frank','harry','suzy']:
 p=B/(n+'-accepted.json');assert json.loads(p.read_text())['accepted']
 shutil.copy2(p,B/(n+'-preboot-accepted.json'))
for n in ['frank','harry','suzy']:idle(n)
manifest=json.loads(Path('/root/zedbiz-maintenance-archives/2026-10-23/manifest.json').read_text())
assert len(manifest)==9 and all(r['contentCompared'] for r in manifest)
for r in manifest:assert Path(r['archive']).is_file() and not Path(r['source']).exists()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==(B/'boot-id-before').read_text().strip()
for n in ['frank','harry','suzy']:
 for svc in ['openclaw-'+n,'zedbiz-asana-mcp@'+n]:run(['systemctl','is-enabled',svc])
run(['systemctl','is-enabled','caddy'])
emit({'readyForReboot':True,'archives':len(manifest)})
