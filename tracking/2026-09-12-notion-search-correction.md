# Notion search diagnosis and correction

2026-09-12 MDT | Cody | Complete: all fourteen agents passed actual AI search and returned-page reading

## What actually failed

The earlier statement that agents could only read known Notion links was incorrect. The existing Codex Apps Notion search entry point works and returns AI-search results. The test stopped at a naming mismatch instead of exercising that supported entry point.

The connected account's self-check reported ai_search available, while the callable tool list exposed notion_search but no separately named ai_search. Its description directed agents toward the absent name. The upgrade verification prompt made that worse by expressly forbidding the existing search route and accepting a known-link read instead. Cody accepted this as an operational limitation without testing the actual available search command.

This was a routing-instruction and verification error. Live tests do not support the previous implication that the Notion account, plan, OAuth connection or OpenClaw 9.4 search capability was broken. The precise reason the separately named alias is omitted by the client catalog is not established; it does not prevent the documented existing search entry point from working.

## Evidence and solution

- [Official Notion supported-tool documentation](https://developers.notion.com/guides/mcp/mcp-supported-tools) states that a keyword content search sent to notion-search runs AI search when the connection can use it and returns type ai_search. Exact filters or non-relevance sorting can select workspace search instead.
- Cody's existing connected search call returned type ai_search and three results.
- Suzy independently called her own existing governed Codex Apps search connection, received type ai_search with three results and fetched a returned page successfully.
- After the persistent instruction correction, a fresh Suzy conversation received only a normal request to find the OpenClaw update procedures. She used the correct search entry point, returned ten AI-search results and opened the VPS2 update procedure, page 37ca3e33-d581-80f9-bdaa-c636ed645102, without a supplied link or search-command coaching.
- The solution adds a small Notion search routing note to each updated agent's existing AGENTS.md. It uses the same approved Sol/Codex OAuth connection, respects real access errors, checks the returned search type and requires opening a result. It does not introduce another account, connector, token or service.
- The upgrade verification prompt now requires a real search and a fetched result. A known-link read alone cannot pass the search check.

## Scope and source

Jack requested diagnosis, a solution and repair after the fourteen-agent 9.4 deployment. Suzy was the pilot. After her fresh-session acceptance passed, the correction was applied to Terry, Edith, Amanda, Marsha, Maggie, Inga, GohZed, Grogar, Wilma, Victor, Vivian, Harry and Frank. No host restart or package change was required.

- Runtime note: [notion-search-route-note.md](../ai-agent-sops/shared-scripts/notion-search-route-note.md).
- Reversible application and fresh-session test helper: [notion-search-route-repair.py](../ai-agent-sops/shared-scripts/notion-search-route-repair.py).
- Corrected upgrade test: [openclaw-94-fleet-verification.txt](../ai-agent-sops/shared-scripts/openclaw-94-fleet-verification.txt).
- [Workstream and authorization](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/311).

The initial helper stopped safely at Maggie's existing heading preamble before changing her file. It was corrected to locate the first Markdown title without removing the preamble. The remaining files then applied successfully. All old instruction bytes outside the inserted note are preserved; per-agent before/after hashes and original files are retained.

## Verification and recovery

All fourteen fresh-session tests passed. Each actual saved search response reported type ai_search and ten results, and a subsequent successful fetch opened a page ID present in that result set. The read-only transcript auditor verified these receipts independently of the agents' final summaries; no Notion tool failure appeared in those sessions.

| Agents | Actual results | Opened returned page |
|---|---|---|
| Terry, Edith, Amanda, Marsha, Maggie, GohZed, Grogar, Wilma, Victor, Vivian | Each: ai_search, 10 results, successful fetch | VPS1 procedure: 37ba3e33-d581-8165-84cd-f6b622a0d944 |
| Inga, Harry, Suzy, Frank | Each: ai_search, 10 results, successful fetch | VPS2 procedure: 37ca3e33-d581-80f9-bdaa-c636ed645102 |

The request was to find OpenClaw update procedures generally, so either server's procedure was a relevant search result. No target page link was supplied in the fresh-session acceptance prompt.

- VPS1 backup and proof root: /home/jackadmin/openclaw-backups/notion-search-20260912/AGENT.
- VPS2 backup and proof root: /root/openclaw-fleet94-20260912/notion-search-repair/AGENT.
- Each directory contains AGENTS.md.before, instruction-audit.json, fresh-agent-search.json and actual-search-receipts.json. VPS1 also retains the compact fleet-search-proof.json summary.
- [audit-notion-search-proof.py](../ai-agent-sops/shared-scripts/audit-notion-search-proof.py) reads only the specified acceptance session's SQLite transcript and extracts search type/count, returned IDs and successful fetched-page receipts. It handles both structured native responses and escaped container page receipts without printing page contents.
- Rollback only this correction by removing the exact inserted routing section. Restore the whole backup only when the current file still matches the audited updated hash, so later instruction changes are not lost. Preserve file ownership and permissions.
- Models, credentials, publishing destinations, permissions and all other instructions remain unchanged by this repair. Any access denial must still be handled as an actual access problem.
