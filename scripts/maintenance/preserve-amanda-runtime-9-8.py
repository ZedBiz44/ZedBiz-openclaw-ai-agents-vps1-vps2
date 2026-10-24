from pathlib import Path
import json,subprocess,os

root=Path('/app/dist')
assert json.loads(Path('/app/package.json').read_text())['version']=='2026.9.8'
onboarding=(root/'onboarding-welcome-BWPRCRYP.mjs').read_text()
assert 'lane: "system-agent-inference"' in onboarding
assert 'timeoutMs: resolveAgentTimeoutMs({ cfg: plan.runConfig })' in onboarding
# These two historical repairs are now upstream. Preserve only Amanda's existing
# policy against aborting live owners merely because elapsed silence is long.
p=root/'diagnostic-stuck-session-recovery.runtime-U0lZegvb.mjs'
text=p.read_text()
needle='\t\tconst preAbortActiveTaskIds = new Set(getCommandLaneActiveTaskIds(sessionLane));'
guard='''\t\tif (activeSessionId || (activeWorkSessionId && isEmbeddedAgentRunActive(activeWorkSessionId)) ||
\t\t\t(sessionLane && getCommandLaneSnapshot(sessionLane).activeCount > 0)) {
\t\t\treturn reportRecoveryOutcome({
\t\t\t\tstatus: "skipped", action: "observe_only", reason: "active_work_no_elapsed_cutoff",
\t\t\t\tsessionId: params.sessionId, sessionKey: params.sessionKey,
\t\t\t\tactiveSessionId: activeSessionId ?? activeWorkSessionId
\t\t\t});
\t\t}
'''
if 'active_work_no_elapsed_cutoff' not in text:
 assert text.count(needle)==1
 updated=text.replace(needle,guard+needle)
 candidate=p.with_name('.'+p.name+'.candidate.mjs')
 candidate.write_text(updated)
 subprocess.run(['node','--check',str(candidate)],check=True)
 os.chmod(candidate,p.stat().st_mode)
 os.replace(candidate,p)
assert p.read_text().index('active_work_no_elapsed_cutoff')<p.read_text().index(needle)
print('Amanda 9.8: upstream inference lane/configured timeout and retained live-owner protection verified')
