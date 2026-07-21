# VPS1 Post-Update Doctor Audit

Date: 2026-07-14 Mountain Time  
Verified by: Cody  
Status: Operational with follow-up findings  
GitHub issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/63

## Scope

Verify all eleven VPS1 agents after the OpenClaw v2026.7.1 rollout, per-agent 1Password startup repair, and human OpenAI Codex OAuth renewal.

Agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.

## Verified Working

- Every agent reports OpenClaw image label `2026.7.1`.
- Every systemd service is enabled and active.
- Every container is Docker-healthy with restart count zero.
- Every local health endpoint returns HTTP 200.
- Every public `agent.zbiz.ca` route returns HTTP 200.
- Every Discord provider connected under the expected agent identity.
- Every `.env.resolved` contains zero unresolved `op://` references.
- Every `.env.resolved` is owned by `1001:1001` with mode `600`.
- Every named `openai:jzedbiz@gmail.com` profile passed a direct live request using `openai/gpt-5.6-sol`.
- Effective authentication order places the named OpenAI profile before `openai:api-key-backup` where the backup exists.
- OpenClaw post-upgrade compatibility checks returned no findings.

## Doctor Method

Ran the read-only command on every agent:

```text
openclaw doctor --lint --severity-min warning --json
```

Did not run `doctor --fix` or `doctor --repair`. Automatic repair could disable intentionally enabled skills or change communication and security policies without review.

## Doctor Findings

### Fleet-Wide

- `openclaw.json` contains plaintext secret-bearing fields.
- The gateway binds to LAN.
- The Policy plugin is enabled without a `policy.jsonc` artifact.
- One or more enabled optional skills have unmet binary or environment requirements.

### Most Agents

- Discord direct messages are open.
- Discord group policy is open.
- Multiple DM senders share the main session scope.

Inga and Vivian did not report these open Discord-policy warnings.

### Agent-Specific

- Marsha's `AGENTS.md` exceeds the bootstrap limit and is truncated.
- Wilma's `openai:api-key-backup` failed with HTTP 401. Wilma's named OAuth profile works and remains first, so she is operational but lacks a working paid backup.
- Terry's named profile is represented as a static stored profile by the status command, but its direct live request passed.

## Decision

Do not apply a fleet-wide automatic Doctor repair. Treat the warnings as a separate controlled cleanup workstream and test corrections on one agent first.

## Recommended Follow-Up Order

- Repair Wilma's API-key backup from the approved 1Password source and verify OAuth remains first.
- Decide whether to deploy a canonical `policy.jsonc` or disable the unused Policy plugin.
- Confirm intended Discord DM and guild policies before changing them.
- Migrate plaintext configuration secrets to supported SecretRefs.
- Disable unused unavailable skills or install only the requirements that each agent actually needs.
- Shorten or split Marsha's bootstrap file without losing mandatory operating rules.

## Rollback

No live configuration was changed during this audit, so no rollback is required.
