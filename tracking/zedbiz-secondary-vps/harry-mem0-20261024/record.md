# Harry Mem0 model migration — 2026-10-24

Owner: Cody. Authorized by Jack to replace the retired memory-processing model with GPT-6 Luna if suitable and verify it. Issue #484. Scope is Harry on VPS2 only.

## Diagnosis and selection

Live Mem0 1.2.1 uses mem0ai 3.0.7 in the pinned g-1e5cd6aa3ff70dae generation. Its configured LLM was gpt-4.1-nano-2025-04-14. OpenAI's [Nano model page](https://developers.openai.com/api/docs/models/gpt-4.1-nano) marks it shut down. [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) is intended for focused high-volume work; standard prices are $0.10 per million input tokens and $0.50 output. Nano's listed historical prices were $0.10/$0.40, so this is not a claim of lower cost than Nano.

The installed OpenAI adapter uses Chat Completions JSON responses for memory inference and does not forward temperature from config. Luna worked through this unchanged adapter; no endpoint, package, reasoning, credential or embedding change was needed. Harry's main conversation model remains openai/gpt-6.1-sol. Shared Qdrant collection mem0_vps1_agents, user zedbiz-vps1, text-embedding-3-small, custom instructions, automatic capture/recall and compatibility guards remain unchanged. Edith and Terry were not modified.

## Pilot

Used the actual installed SDK with the same backend and credentials and a separate synthetic user scope cody-harry-luna-pilot-20261024. Inferred a weekday fact, searched it, inferred a correction, then searched again. Both API responses identified gpt-6-luna, taking 2.665 and 8.857 seconds. The corrected fact ranked first. The earlier fact remained as a second record; this proves capture and corrected recall, not in-place reconciliation. Both synthetic records were ownership-checked, individually deleted and an empty filtered result verified.

Qdrant proxy version-discovery warnings persisted while all reads/writes succeeded. Initial local SSH quoting failed before execution and was corrected using a script. No production data was changed during pilot except the isolated test records, which were removed.

## Deployment and recovery

Protected evidence directory: /root/cody-harry-mem0-20261024 (0700). Saved openclaw-before.json (0600), waited for active work to drain, stopped only Harry, changed only the model field, compared all remaining config fields, then started Harry. Config SHA256 before a220cc0a1b6f52d711fa8daeee723626935dff4d591a60d99feb58b6a669cd51; after 24e34e83381e676dfe717eaabaf1766c166ca4e450dee524ac0dbd3233cb439b.

The accompanying JSON Patch records the exact single-field change; it contains no secrets. Dated scripts are execution evidence, not a general SOP. No maintained SOP changed. Rollback can restore the saved config after preserving later changes, but the old retired model is not a usable recovery target; use a verified supported model for a forward fix if required. No vector or embedding migration occurred.

## Final verification

Passed: actual Harry turn 0f115af1-8adc-4d10-91cd-9581f2c6146d successfully called mem0_search and recalled an existing ZedBiz operational fact. Effective conversation model gpt-6.1-sol, rerouted=false. Mem0 1.2.1 loaded, CLI health passed and public HTTPS returned 200. Gateway logged automatic capture of one memory at 11:13:27 MDT after the configuration switch. No automatic service restart or OOM occurred. Frank and Suzy remained active.

Startup included approximately 93 seconds in plugin loading and another slow runtime-loading interval; probes waited for readiness. One automatic recall hit its existing eight-second limit during warm-up; memory injection and the explicit search succeeded, followed by successful automatic capture. This task does not claim to fix the pre-existing startup/recall latency behavior or establish long-term throughput. No endpoint or adapter code changes were made.

Machine-readable pilot and acceptance evidence is retained alongside this record. Daily Cody journal: https://www.notion.so/403a3e33d581812c80e7c83e0772450c . Deployment complete; source record is proposed via cody/harry-mem0-luna-20261024 for review rather than merged automatically.
