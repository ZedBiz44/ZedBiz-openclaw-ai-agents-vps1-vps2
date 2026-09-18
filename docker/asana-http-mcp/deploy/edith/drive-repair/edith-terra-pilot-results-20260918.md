# Edith Drive repair and Terra pilot — September 18, 2026

Status: Session A complete; Session B running. Times below are Mountain Daylight Time.

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

Started at 2:05:59 p.m. Native model records confirm GPT-5.6 Terra with medium reasoning. It uses the tested continuous phase runner for unfinished duplicate rows and preserved Photoshop files, followed by one final reconciliation. Results pending.

## Assessment limits

This is a real work pilot with workflow fixes made during execution, not a controlled model-only comparison. Session A required intervention. No permanent default-model change or recurring restart was enabled. The prior default remains in place pending the second session's result.

