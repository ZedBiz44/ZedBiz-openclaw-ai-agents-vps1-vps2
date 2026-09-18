# Edith Drive repair and Terra pilot — September 18, 2026

Status: Both sessions complete; repair verified; Laughs And Fun ready for Ruby's independent review. Times below are Mountain Daylight Time.

## Confirmed repair

The installed GOG client allowed only 30 seconds for response headers. Three historical copy requests had succeeded on Drive despite timeout reports. All three were reconciled and verified without another copy. Edith's scoped copy client now allows 120 seconds for headers and disables blind write retries. Read-only reconciliation must find one exact recent matching copy before work continues. Uncertain outcomes remain held.

Unit tests, Google API/copy tests and a real HTTP server delaying headers for 31 seconds passed. Session A completed 160 new copies with no new GOG errors or timeout recovery needed. This verifies the installed behavior; it does not guarantee that Google Drive will never time out.

## Session A

- Runtime confirmed from native model records: GPT-5.6 Terra, medium reasoning.
- Start 1:29:01 p.m.; finish 2:04:57 p.m.; elapsed 35 minutes 56 seconds.
- New verified copies: 160. Additional archived originals: 202.
- Ending state: 488 source proofs, 485 unique active files, 488 archived originals, zero pending writes.
- Actual input tokens: 15,054,761, including 14,824,448 cached input; fresh input 230,313. Output 30,125, including 6,702 reasoning tokens. These are runtime token counts, not a dollar invoice or subscription usage percentage.
- The initial generated loop unnecessarily selected completed rows. Cody stopped only that read-heavy subprocess at a safe boundary, keeping the model session alive. Edith then completed unfinished direct-source exports.
- Forty duplicate originals remained because they needed their own source-ID proofs pointing to existing canonical copies. The tested duplicate-proof helper is installed for Session B; no duplicate output was created to work around the check.
- An attempted in-session control command required authorization and was not used. A normal correction message queued until the run ended and caused one redundant read-only follow-up on the default Astra model. It ended without file changes. The follow-up consumed 51,380 fresh input, 171,136 cached input and 910 output tokens; count it as operator overhead, not Terra output. A stop request did not interrupt it; the session-wide request returned unauthorized. No authorization settings were changed.

## Session B

- Native model records confirm GPT-5.6 Terra with medium reasoning. Start 2:05:59 p.m.; finish 2:41:27 p.m.; elapsed 35 minutes 29 seconds.
- Forty duplicate aliases were verified and archived without new copies, in 3m31s.
- The 250 Photoshop copies and retained originals completed in 24m31s. No downloads, renders, conversions or filename changes. No copy errors.
- One fresh final inventory checked 1,711 items and 122 recorded folder paths. All 778 planned originals/proofs, 735 unique active files, checksum/size and destination/retention checks passed. Two missing historical alias crosswalk entries were repaired from live verified existing copies with no Drive mutation.
- There are 43 actual duplicate aliases. The saved crosswalk dictionary has 83 entries because it also contains 40 canonical self-mappings; 83 is not the number of duplicates.
- Input tokens 7,968,709, including 7,767,808 cached input; fresh input 200,901. Output 17,625, including 5,129 reasoning tokens. Full reconciliation and handoff are included.
- The existing handoff helper initially lacked its sibling-module import path. Edith corrected the invocation within the same session and verified the release. No recurring scheduler was enabled.
- Ruby's assignment was independently read back: https://app.asana.com/1/11298561585567/project/1218559074752632/task/1218643266765994 . Parent remains incomplete pending Ruby: https://app.asana.com/1/11298561585567/project/1218559074752632/task/1218559788929226 . Assignment is verified; reviewer pickup and acceptance are not claimed here.
- No active Edith session remained after the pilot. The old periodic dispatcher pause remained present. No next-folder work was started.

## Recommendation

Keep the tested executor, unfinished-row filtering, full-metadata listings, evidence reuse and Photoshop shortcut. Continue using Terra medium for prepared execution work under independent review; do not claim this proves equal quality for new classification or complex planning. The first session required operator correction and the file mixes differ. The principal supported improvement is moving routine operations into the tested script and eliminating restart/reinspection overhead. Leave the global default unchanged for now; this authorization was a two-session trial, not a permanent model migration.

Across both sessions, 410 new copies completed with zero logged GOG errors. All three historical uncertain copies were recovered separately without replay. Twelve focused Python tests and the scoped GOG tests passed. Future folder tasks should be sized by unique content, file types, required judgment and natural groups before task creation, with checkpoints but no forced time-based restarts.

## Assessment limits

This is a real work pilot with workflow fixes made during execution, not a controlled model-only comparison. Session A required intervention. No permanent default-model change or recurring restart was enabled. Ruby's independent acceptance and the remaining main folders are outside this completed technical pilot; this does not close the whole Edith project.

