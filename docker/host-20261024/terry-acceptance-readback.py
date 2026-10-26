"""Keep the failed all-tools gate visible; report actual saved-route capabilities separately."""
import pathlib,json,subprocess,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024')
r=json.loads((W/'acceptance-terry-live/tools.json').read_text());receipt=r['result']['meta']['agentMeta']['terminalReceipt'];assert r['status']=='ok' and not receipt.get('rerouted')
route=json.loads((W/'terry-route-check.json').read_text());override=route['checkpointContainsExistingMainSessionOverrides'];assert override['modelOverrideSource']=='user' and receipt['effective']['model']==override['modelOverride'] and receipt['effective']['provider']==override['providerOverride']
tools=set(receipt['successfulToolNames']);assert 'mem0_search' in tools and 'asana__asana_get_user' in tools
p=subprocess.run(['docker','exec','terry','gog','--readonly','--no-input','--json','drive','ls','--max','1'],capture_output=True,text=True,timeout=120);(W/'acceptance-terry-live/drive.log').write_text(p.stdout+p.stderr);assert p.returncode==0
proof={'modelResponsePassed':True,'actualModelMatchesPreRebootUserOverride':True,'model':receipt['effective'],'memoryRecallPassed':True,'asanaOwnIdentityPassed':True,'authenticatedDriveReadPassed':True,'requestedCodexNotionRouteVerified':False,'allToolsGatePassed':False,'limitation':'Saved user DeepSeek main-session override uses the direct-provider lane; Codex session read/write tools are disabled by existing supervision settings. No configuration or user override changed.','receipt':receipt}
(W/'terry-acceptance-readback.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

