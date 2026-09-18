# Edith uninterrupted-work test
Date: 2026-09-17 Mountain Time | Agent: Cody | Status: Test finished; production paused on Drive errors

## Result
The observed production session continued across the former12-minute useful-work limit and15-minute worker limit without another task, external supervisor restart or full-project reload. It ended naturally after20m21s because Drive copy requests failed in two groups, not because of the former timer. This supports Jack's criticism of the forced restart design. It does not establish that the historical two-hour halt is resolved.

## Observed output
- Start: September17,10:50:55.929p.m.Mountain. Native completion:11:11:17.254p.m.
- Same active run throughout:91c56932-cc9c-4403-94b5-9027a02d35cb.
- Existing session:f5e6597e-3c05-4b5b-b32e-4832c1270823 / agent:main:edith-project-continuous-1218611177927226.
- Source-copy records243→326; unique active outputs240→323:83 new verified copies.
- Original archive records243→286:43 newly archived originals.
- Four logo files and39 Learning01 images fully copied/verified/archived.
- Forty Happiness images copied/verified; originals remain untouched in their source folders.
- No new dispatch task, no successor and no full-folder final-audit file at ordinary checkpoints.
- Drive calls:481 get,94 ls,175 permissions,7 mkdir,84 copy attempts,83 download,43 move. There were no new conversions or changes to protected items.
- Final session status done, abortedLastRun=false. No running main-agent sessions at final check. Backup1218611357802915 remains cancelled. Old dispatcher remains paused.

## Why it stopped
Two Google Drive copy calls timed out awaiting HTTP/2 response headers, in different groups. The executor saved uncertain-write records. No blind copy retry occurred.
- Source18X5vP3cFzKGIahrYYv44oFXWG7nwVZZj: destination search found no matching output, which does not prove the copy failed; remains uncertain.
- Source1zyJNr1GHEGrzWjcp92YEser7U-Ti-gAC: exactly one matching output1Cr-VXq6WHtX_gwUzrZTeNblrSASZWMub was found and verified by content/checksum/location/access without copying again; saved proof is included in the83.
Edith stopped further writes after the repeated error, left all originals intact, and reported exact reconciliation requirements to Amanda. The older DOCX hold and InCanmore rename restriction are unchanged.
Asana parent report story1218612926629952 and dispatch report1218617767685021 were read back from Edith's own successful tool results. Parent1218559788929226 remains incomplete and not Ready for Review.

## Startup complication and limits
The first client attempt ran before the gateway was ready and returned ECONNREFUSED with unchanged counts. Starting the service also activated OpenClaw's built-in restart recovery on the original interrupted session. Two attempts to submit a new turn to that same key returned SESSION_WORK_START_CHANGED before work.
One separate fresh test session then started, detected the existing writer, performed reads only and returned. It did not mutate Drive. Cody identified the recovered original session, verified it had read the revised test brief/task, and observed it as the sole remaining production writer. This was not a clean laboratory startup; the extra read-only session's usage must not be hidden.
The old dispatcher and newly built continuous controller were not running this production turn. No second production writer was launched. Read-only observers queried saved records and did not invoke the LLM.

## Usage measurements and comparison limits
Completed production run:171,598 uncached input tokens,7,854,848 cached input tokens,23,804 output tokens. Native total input8,026,446 includes cached input; do not count it twice.
Extra read-only test session:90,504 uncached input,1,068,160 cached input,3,428 output.
Combined observed test model use:262,102 uncached input,8,923,008 cached input,27,232 output. Failed pre-work attempts, gateway initialization and other service/provider costs are not a dollar bill and are not fully represented by these model counters.
Recent four short production runs made107 new copies over38m52s of worker time, or45m31s including intervening gaps. Their totals were462,593 uncached input,14,930,688 cached input and45,439 output. This test produced83 copies in20m21s, but only43 original archive moves finished before the hold. Different file mixes and unfinished archiving make an overall speed/cost multiplier unjustified.
Per verified-copy token counts were lower in this sample even including the extra read-only session, but this is not proof of equivalent complete-folder savings. Cached tokens are not equivalent to fresh input or account quota percentages.

## Next action
Keep forced short-session restarts and dispatch chaining off. Preserve checkpoints and allow meaningful groups to continue in the same session.
Investigate the specific GOG/Google Drive HTTP/2 copy timeout and reconcile the unresolved write before resuming mutations. Do not redesign the whole workflow or reinstate a timer in response.
After write-route reliability is addressed, reuse saved output IDs; archive the40 Happiness originals and map their40 duplicate originals without additional copies. Then continue160 remaining ordinary JPEGs and250 Photoshop originals under the existing exceptions.
No new executor was built for this test. No further production restart was queued. Ruby's existing review scope and independent acceptance remain unchanged.
