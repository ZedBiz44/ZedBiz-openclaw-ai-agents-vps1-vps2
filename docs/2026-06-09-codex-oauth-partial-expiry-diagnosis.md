# Codex OAuth Partial Expiry Diagnosis

**Date:** 2026-06-09
**Recorded by:** Manus
**Status:** Diagnosed -- Action Required

---

## Summary

Five agents are showing Codex OAuth errors while five others continue working normally. The root cause is a **shared refresh token** that was copied across multiple agents during a batch setup around May 28, 2026. When the access token expired on June 7, the shared refresh token could not auto-renew for all agents simultaneously -- OpenAI's OAuth system invalidates a refresh token after it is used once, so only the first agent to attempt a refresh succeeded (or none did, leaving all five stuck).

The five working agents were individually re-authorized around June 7, each receiving their own unique refresh token. Their access tokens now expire June 17.

---

## Agent Status Table

| Agent | OAuth Status | Access Token Expires | Refresh Token | Net Effect |
|---|---|---|---|---|
| terry | Valid | 2026-06-17 08:00 | Unique | Working normally |
| amanda | Valid | 2026-06-17 08:05 | Unique | Working normally |
| inga | Valid | 2026-06-17 08:16 | Unique | Working normally |
| marsha | Valid | 2026-06-17 08:40 | Unique | Working normally |
| wilma | Valid | 2026-06-17 08:45 | Unique | Working normally |
| gohzed | **EXPIRED** | 2026-06-07 06:40 | **Shared (same as grogar/maggie/victor/vivian)** | OAuth error on Codex models |
| grogar | **EXPIRED** | 2026-06-07 06:40 | **Shared** | OAuth error on Codex models |
| maggie | **EXPIRED** | 2026-06-07 06:40 | **Shared** | OAuth error on Codex models |
| victor | **EXPIRED** | 2026-06-07 06:40 | **Shared -- NO api-key fallback in auth-profiles** | OAuth error, potentially harder to recover |
| vivian | **EXPIRED** | 2026-06-07 06:40 | **Shared** | OAuth error on Codex models |

---

## Root Cause

All five expired agents share the **identical refresh token** (prefix: `rt_kwaXVjmmEdXrOJ9xm4PfjQJb_SV...`). This token was originally issued on **May 28, 2026** and was copied to multiple agents as part of a batch setup procedure.

OpenAI OAuth refresh tokens are **single-use** -- once one agent uses the refresh token to get a new access token, the refresh token is rotated and the old one is invalidated. With five agents holding the same refresh token, the auto-refresh race condition means none of them successfully renewed, and all five are now stuck with expired tokens.

The five working agents (terry, amanda, inga, marsha, wilma) each have **unique refresh tokens** (all prefixed `rt.1.AAC...` or `rt.1.AAB...`), indicating they were individually re-authorized through the browser OAuth flow.

---

## Fix Required

Each of the five expired agents needs to be individually re-authorized through the Codex OAuth browser flow. There is no way to copy a token from a working agent -- each agent must go through its own OAuth handshake to receive its own unique refresh token.

**Agents needing re-auth:**
- gohzed
- grogar
- maggie
- victor
- vivian

**Note on Victor:** Victor's `auth-profiles.json` does not include the `openai:api-key-backup` profile (even though `openclaw.json` lists it in the order). This means Victor has no fallback at all and is completely blocked on any OpenAI model until re-authorized.

---

## Lesson Learned / SOP Update

The SOP for agent creation must be updated to note that **OAuth tokens cannot be batch-copied** across agents. Each agent must go through its own individual OAuth browser authorization. The existing SOP note about "copying OAuth from an existing agent" should be clarified to indicate this only works for the initial access token (short-term) and will fail at the first refresh cycle (~10 days).

Going forward, all agents should be authorized individually and the unique refresh token prefix should be verified to confirm each agent has its own token.
