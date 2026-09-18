# Edith efficiency investigation and proposed replacement
Date: 2026-09-17 Mountain Time | Agent: Cody | Status: Edith stopped; recommendation awaiting approval

## Recommendation
Use AI to make naming and organization decisions, then let one reusable program carry out the approved file plan without an LLM supervising every small batch. Asana should track folder delivery, exceptions and Ruby's review. It should not schedule routine file-processing sessions. Do not restart the continuous controller merely with a longer timer.

## Verified stop
Edith's container exited at 9:15:44 p.m. Mountain; Docker reported Running=false and Pid=0. The scheduled backup task1218611357802915 is cancelled/completed as a scheduling record only. A production-paused-by-jack.json marker blocks new dispatcher admission. The active task1218611177927226 and folder parents are not accepted/completed by this stop.
The supervisor was suspended first. Two gateway chat.abort calls returned unauthorized; stopping Edith's container stopped her agent processes without changing credentials or other agents. Container restart policy is unless-stopped. Saved state remains on mounted storage. No new implementation or restart is authorized by this investigation.

## What the evidence shows
The last completed worker1218626138762463 ran9m45s. Its operations log contains25 copy calls,27 archive moves and740 metadata reads, with906 total logged Drive commands. The final verification fetched574 items. Comparison against the previous saved verification shows518 IDs had already been checked and all518 metadata records were unchanged; only56 IDs were new.
Across the four latest completed workers, final recheck size grew395,466,518,574 while new copy calls were27,32,23,25. The verify-sitting scripts explicitly fetch every saved source, output and folder after each sitting. This makes later batches pay again for earlier completed work.
The last worker started9:02:05p.m.; first logged Drive operation9:04:18, first successful copy9:04:48, last Drive result9:10:45 and worker exit9:11:50. This includes substantial startup/reporting overhead, but these timestamps alone do not precisely separate model time, tool waiting and useful planning.
The execution guard rechecks the entire778-file plan and hashes all evidence before each mutation. A read-only benchmark of one actual saved copy gate took0.214s,781 hash calls,358 unique files and82.9MB hashed. This is wasteful repeated local work, but it is not by itself an explanation for ten-minute runs.
The executor also lists the same destination repeatedly for collisions, fetches per-file source/destination permissions, and downloads/opens every new binary copy despite already comparing Drive checksums and having prior source inspection. Some checks are necessary; their repetition and placement need redesign.
The last completed run reported129,783 input tokens,11,387 output tokens and3,753,600 cache-read tokens across the run. Cached traffic is not equivalent to fresh input, a dollar bill or account-limit consumption. No dollar or percentage saving is claimed.
Existing state records243 source-copy proofs and243 archived originals; the checkpoint reports240 unique active outputs because some sources share canonical copies. One known uncertain DOCX copy from8:19p.m. remains held. The5 InCanmore renames remain blocked by the scoped guard. These are separate exceptions, not reasons to recheck every completed file.

## Proposed operating workflow
- Edith loads the current folder inventory and existing saved decisions once. For Laughs And Fun, reuse the existing778-row plan and inspected evidence after freshness checks; do not start classification over.
- For new folders, inspect content in coherent groups/contact sheets, make one structured naming/destination plan, and send only ambiguous items back for judgment. Preserve Photoshop and intact-package exceptions. Normal useful documents and images still receive the content inspection needed for correct organization.
- A reusable program validates the immutable plan/evidence once at job admission. Per operation, enforce the approved source, exact destination, protected boundaries and relevant current source revision. Invalidate the admitted plan if its inputs change. Do not weaken the gate or let a cached approval apply to changed material.
- The program runs the remaining approved queue directly, saves each confirmed result and resumes by source ID after interruption. Keep a single writer. No ad-hoc script writing or LLM call is required between ordinary copy/check/archive operations.
- Verify new or changed results as they are produced, then perform one complete folder reconciliation before submission. Do not fetch every completed source/output/folder after every small batch.
- List each destination with the required metadata once per phase and maintain a collision index under the writer lock; refresh when external changes or conflicting results are detected. Keep exact revision/access checks for affected files. Parallelize bounded read-only metadata requests, not competing writers.
- For binary files whose source content was already inspected and whose source revision and source/copy checksums match, propose reusing that content proof rather than downloading/decoding the identical copy again. Native Google documents, missing checksums, changed sources and actual discrepancies require their own checks. This is a scoped procedural change to approve and test, not an exemption from source inspection.
- Publish one compact Asana progress update at a meaningful folder milestone or exception. Release Ruby on Ready for Review; Ruby retains every level1/2 folder check, five file samples and the quick duplicate scan. Amanda owns actual exceptions, not polling.

Google documents partial-field retrieval, batch requests and binary checksum fields. Batch requests do not remove per-operation quota usage or replace safe ordering. Start with the approved existing Drive route; check its exposed support before changing a connector. No new OAuth, credentials or permissions are proposed.
Sources: https://developers.google.com/workspace/drive/api/guides/performance ; https://developers.google.com/workspace/drive/api/guides/fields-parameter ; https://developers.google.com/workspace/drive/api/reference/rest/v3/files

## Exactly what would change
- Cody: replace ad-hoc per-sitting execution and full-repeat audits with a tested persistent batch executor; retain the mutation journal, copy-first original retention, source revision checks, collision checks, holds and one-writer lock.
- Cody: update the project-specific files-and-folders execution guidance to distinguish source content judgment, copy integrity and independent review; unchanged byte-identical binaries need not be visually judged twice.
- Cody: retire normal dispatch chaining/continuous LLM supervision; use a non-LLM job receipt/status for progress and an explicit exception on failure.
- Edith: classify unresolved material and resolve real exceptions. Avoid repeated memory/whole-project reloads and writing new batch scripts.
- Asana: keep existing folder tasks, coordinator assignment and approvals. No new project, per-file tasks, heartbeat or paid AI workflow.
- Ruby: retain Jack's agreed review depth. No repeated readiness checks or full-file audit.

## Pilot and acceptance before broad restart
Prepare and test the executor against saved fixtures while Edith stays stopped. After approval, reconcile the known uncertain write and any interrupted operations read-only; do not retry blindly.
Run one representative set of25–50 not-yet-processed, already-classified files through the approved route. Use a recorded fixed plan and compare with the observed25-copy/9m45s baseline, while accounting for different sizes/types.
Measure elapsed time, new copies, API calls, downloaded bytes, LLM calls and usage, duplicate prevention, retained originals and reviewer findings. The execution phase should make zero LLM calls and zero normal dispatch tasks. Inspect changed items only between checkpoints; allow one full final folder reconciliation.
The saved latest-run audit demonstrates518 repeated unchanged reads. Replacing its574-item checkpoint audit with the56 changed/new IDs would remove518 of that run's906 calls, about57%, before other optimizations. This is a replay-based request-count estimate, not a speed or cost guarantee; final folder verification still occurs.
Prove safe interruption/resume, changed-source detection, name collision handling, protected-file rejection and uncertain-write hold. Then Ruby reviews the output. Report actual results and get the restart decision before broader production; do not label a code test as live throughput proof.

## Current decision
Approve building and testing this batch-executor approach, including the scoped verification changes, before a controlled live pilot. Edith remains stopped until Jack explicitly authorizes restart. No files will be reorganized during diagnosis.
