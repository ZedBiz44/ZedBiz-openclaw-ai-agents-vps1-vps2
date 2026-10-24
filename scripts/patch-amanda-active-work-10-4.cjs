const fs=require('node:fs');
const file=process.argv[2];
let source=fs.readFileSync(file,'utf8');
const needle='\t\tconst preAbortActiveTaskIds = new Set(getCommandLaneActiveTaskIds(sessionLane));';
const guard=`\t\tif (activeSessionId || (activeWorkSessionId && isEmbeddedAgentRunActive(activeWorkSessionId)) ||
\t\t\t(sessionLane && getCommandLaneSnapshot(sessionLane).activeCount > 0)) {
\t\t\treturn reportRecoveryOutcome({
\t\t\t\tstatus: "skipped", action: "observe_only", reason: "active_work_no_elapsed_cutoff",
\t\t\t\tsessionId: params.sessionId, sessionKey: params.sessionKey,
\t\t\t\tactiveSessionId: activeSessionId ?? activeWorkSessionId
\t\t\t});
\t\t}
`;
if(!source.includes('active_work_no_elapsed_cutoff')) {
 if(source.split(needle).length!==2)throw Error('Unexpected upstream recovery structure');
 source=source.replace(needle,guard+needle);fs.writeFileSync(file,source);
}
if(source.indexOf('active_work_no_elapsed_cutoff')>source.indexOf(needle))throw Error('Guard order wrong');
console.log('Amanda live-owner protection preserved');
