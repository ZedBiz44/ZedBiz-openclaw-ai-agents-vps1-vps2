"""Final live-work gate and authorized server-maintenance reboot."""
import pathlib,json,time,subprocess,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024')
assert json.loads((W/'reboot-checkpoint.json').read_text())['passed']
p=W/'before-reboot-fleet.json';assert time.time()-p.stat().st_mtime<120,'Refresh live-work checks'
fleet=json.loads(p.read_text());assert len(fleet)==11 and all(x['activeWork'] is not None and not any(x['activeWork'].values()) and x['runningSchedules']==0 for x in fleet)
assert not (W/'reboot-intent.json').exists(),'Reboot already requested'
intent={'authorizedBy':'Jack: finish VPS1 server updates','timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'bootIdBefore':P('/proc/sys/kernel/random/boot_id').read_text().strip(),'reason':'Activate updated container helpers and clear old host-library sessions','checkpointVerified':True,'remainingGatewayWorkZero':True,'terryManagedStopped':True}
(W/'reboot-intent.json').write_text(json.dumps(intent,indent=2))
subprocess.run(['systemctl','reboot'],check=True)

