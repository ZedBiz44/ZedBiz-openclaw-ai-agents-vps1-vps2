# 2026-06-17 - Codex OAuth Refresh Method Check

Date | Author | Status: 2026-06-17 | Cody | Completed

## Question

- Manus proposed copying Wilma's fresh OAuth token / SQLite auth profile store entry to expired agents Terry, Inga, and Marsha.
- User suspected this was not the correct refresh method and asked for records plus Technical Documentation to be checked.

## Records Checked

- Notion: `OpenAI Codex OAuth Procedure`
- Notion: `OpenAI-Oath-Provider`
- Notion: `Doctor-june-17-results`
- Local tracking: `2026-06-12-notion-access-diagnosis-amanda-inga-gohzed-maggie-marsha.md`
- Local tracking: `2026-06-12-openai-billing-route-diagnosis.md`

## Finding

- The newer VPS1 `OpenAI Codex OAuth Procedure` is explicit: never copy a token from one agent to another.
- It says OpenAI refresh tokens are single-use, and the first agent to refresh a shared token can burn it for the rest.
- The same page's incident log says a prior shared-refresh-token batch caused Gohzed, Grogar, Maggie, Victor, and Vivian to expire/fail.
- The older VPS2 `OpenAI-Oath-Provider` page does describe copying auth files from Harry to other VPS2 native-install agents, but this conflicts with the newer VPS1 procedure and applies to a different host/runtime layout.
- The current VPS1 agents use SQLite auth state at `~/.openclaw/agents/main/agent/openclaw-agent.sqlite`, not the older VPS2 `auth-profiles.json` copy path.

## Live Read-Only Check

- `wilma`: `openai:jzedbiz@gmail.com` OAuth expires `2026-06-27T08:45:02.103Z`.
- `terry`: `openai:jzedbiz@gmail.com` OAuth expired `2026-06-17T08:00:22.655Z`.
- `inga`: `openai:jzedbiz@gmail.com` OAuth expired `2026-06-17T08:30:10.064Z`.
- `marsha`: `openai:jzedbiz@gmail.com` OAuth expired `2026-06-17T09:00:02.399Z`.
- All four also show `openai:api-key-backup`, so expired OAuth should fall back rather than make the agents completely dark.

## Verdict

- Do not copy Wilma's SQLite OAuth/auth profile entry to Terry, Inga, or Marsha.
- Correct VPS1 refresh method is individual device-code/browser reauthorization for each expired agent.
- Manus can verify token status and run post-refresh checks, but Jack must approve each browser OAuth flow.

## Notion

- Created Tech Updates entry: `2026-06-17 | Cody | Codex OAuth Refresh Method Check`.
