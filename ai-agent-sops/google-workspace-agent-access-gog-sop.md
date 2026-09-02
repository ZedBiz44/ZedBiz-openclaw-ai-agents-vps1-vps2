# Google Workspace Agent Access — GOG SOP

Date: 2026-09-01 | Agent: Cody | Status: Active

## Purpose

Give every authorized ZedBiz agent maximum GOG access to both `jack@zbiz.work` and that agent's own Gmail account, while preserving separate credentials, explicit account routing, human consent, audit evidence, and confirmation gates for consequential actions.

## Final Access Decision

- Every agent receives two independent Google OAuth authorizations.
- `main-google` points to `jack@zbiz.work`.
- `agent-google` points to that agent's individual free Gmail account.
- Both authorizations request GOG's `all-user` service bundle, `--drive-scope full`, and `--gmail-scope full`.
- This replaces the former Drive-only/Gmail-only split and the former `main-drive` and `agent-mail` aliases.
- No additional paid Google Workspace licence is required because the shared Workspace identity remains `jack@zbiz.work`; the individual agent identities are free consumer Gmail accounts.
- Use GOG for OpenClaw agents on VPS1, VPS2, and VPS4.
- Ruby on VPS3 uses Hermes and requires a separately validated two-account implementation; do not force the GOG procedure onto Ruby.
- Test on one canary agent, prove both identities and revocation, then authorize agents one at a time.
- Do not use the Codex Google Drive connector as the credential route for persistent server agents.

## What Full GOG Access Means

Live GOG v0.38.1 checks on 2026-09-01 confirmed that `--services all-user` covers the normal user-OAuth catalogue, including Gmail, Calendar, Chat, Classroom, Drive, Drive Activity, Drive Labels, Docs, Slides, Contacts, Tasks, Sheets, People/Profile, Forms, Sites, Meet, Apps Script, Analytics, Search Console, Google Ads, YouTube, and Photos.

- `--gmail-scope full` grants the maximum GOG Gmail scope.
- `--drive-scope full` grants the maximum GOG Drive scope.
- Some Google/GOG integrations are inherently read-only, including Analytics, YouTube, Photos, Drive Activity, Drive Labels, and Forms responses. “Full” means the maximum available capability for that service, not write access where Google exposes read-only scopes.
- Consumer Gmail accounts may not have Workspace products, organization data, Ads accounts, Analytics properties, Search Console properties, Classroom data, or Shared Drive membership. OAuth permission does not create those entitlements.
- Google Admin SDK, Cloud Identity Groups, and Google Keep are not normal user-OAuth GOG services. They require a service account with Google Workspace domain-wide delegation and a separate administrator-approved SOP.
- Google Photo Picker is an explicit consumer-OAuth opt-in and is not assumed to be included in the default `all-user` bundle. Validate its live syntax and account compatibility separately before adding it.
- Every corresponding Google API must be enabled in the selected Google Cloud project. OAuth scopes alone do not enable APIs.

## Consequences Jack Explicitly Accepted

Authorizing `jack@zbiz.work` this broadly means every authorized agent can potentially:

- Read, send, organize, and modify Jack's Gmail.
- Read and modify Jack's calendars, contacts, tasks, Drive files, Docs, Sheets, Slides, Forms, and other supported Google data.
- Access every My Drive item and Shared Drive item visible to `jack@zbiz.work`.
- Act under Jack's Google identity; Google audit logs will show `jack@zbiz.work`, while the agent name must come from OpenClaw/Hermes execution logs.

Full OAuth permission is capability, not blanket business authorization. Agents must still obtain explicit human confirmation before:

- Sending consequential external communications from Jack's mailbox.
- Deleting, trashing, moving, or broadly reorganizing data.
- Changing permissions, Shared Drive membership, external sharing, or public links.
- Creating, changing, or cancelling meetings with external attendees.
- Publishing scripts, changing Ads, or making other financially, legally, or reputationally consequential changes.

## Confirmed Workspace Boundary

The Shared Drives currently visible to `jack@zbiz.work` are:

- `Z-Administrative`
- `Z-Clients`
- `Z-Core-Ventures`
- `Z-External`
- `Z-Marketing`
- `z-migration`
- `Z-Operations`
- `Z-Prospects`
- `Z-Ventures`

OAuth cannot restrict `jack@zbiz.work` to selected Shared Drives. The account's existing memberships and Google permissions determine actual access.

## Current Live Fleet State

Read-only checks completed 2026-09-01 Mountain Time:

- VPS1: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma are healthy on GOG v0.38.1; GOG is eligible/model-visible; no Google tokens are stored.
- VPS2: Harry, Frank, and Suzy are active on GOG v0.38.1 with no tokens. Their current OpenClaw config contains the unrecognized key `meta.lastTouchedAt`; repair and reverify skill visibility before OAuth.
- VPS3: Ruby's Hermes `google-workspace` v1.2.0 is present; no token exists at `/opt/data/google_token.json`.
- VPS4: Rocky's gateway is active; GOG v0.38.1 is eligible/model-visible; no Google tokens are stored.
- No audited agent is authenticated to Google, and no live Google service test has passed.

## Google Cloud Setup

Use one ZedBiz-controlled Google Cloud project owned by `jack@zbiz.work`.

- Enable every API needed by the live `all-user` catalogue.
- Configure the OAuth audience as External because the free agent Gmail accounts are outside `zbiz.work`.
- Create a Desktop app OAuth client.
- Store the client JSON only in the approved 1Password item.
- Import the same approved client into each agent's isolated token store.
- Never store OAuth JSON, refresh tokens, service-account keys, authorization codes, passwords, or recovery codes in GitHub, Notion, chat, logs, or agent memory.
- Add `jack@zbiz.work` and the canary agent Gmail as test users when the app is in Testing.
- Google External apps left in Testing can issue refresh tokens that expire after seven days for sensitive/restricted scopes. Use Testing only for the canary and resolve the Production/verification design before fleet rollout.

## OpenClaw Two-Account Authorization

Use Marsha as the combined-access canary because her individual Gmail setup is already in progress.

### Preflight

Run inside Marsha's normal protected runtime:

```bash
gog --version
openclaw skills info gog --json
gog auth list --check
gog auth add --help
gog auth services --json
```

Pass only when GOG is current, the skill is eligible/model-visible, the token store is Marsha-specific, no unexpected account exists, and the live help still confirms `all-user`, full Drive, and full Gmail scopes.

### Import The OAuth Client

```bash
gog auth credentials set /secure/temporary/client_secret.json
gog auth credentials list
```

Remove the temporary protected file or mount after import. Never copy another agent's token store.

### Authorize Jack's Workspace Account

```bash
gog auth add jack@zbiz.work \
  --services all-user \
  --drive-scope full \
  --gmail-scope full \
  --manual \
  --force-consent

gog auth alias set main-google jack@zbiz.work
```

### Authorize The Agent's Gmail Account

Replace the example address with the agent's exact Gmail address:

```bash
gog auth add marshazagent@gmail.com \
  --services all-user \
  --drive-scope full \
  --gmail-scope full \
  --manual \
  --force-consent

gog auth alias set agent-google marshazagent@gmail.com
gog auth list --check
```

For each authorization:

- The agent generates the Google URL and pauses.
- Jack opens the URL in a trusted browser and deliberately selects the exact intended account.
- Jack reviews and approves the consent screen.
- Jack returns the full loopback redirect URL through the approved temporary channel.
- Treat the redirect URL/code as sensitive until exchanged; do not record it.
- If Google blocks a scope or displays a warning, stop and document the exact scope and app-publication requirement. Do not silently reduce access and call it complete.

## Mandatory Account Routing

Every GOG command must explicitly name one alias:

- Use `--account main-google` for Jack's Workspace data and Jack's Gmail.
- Use `--account agent-google` for the agent's own Gmail and consumer Google data.
- Do not configure an ambiguous global default.
- Do not infer the account from the service name.
- Never copy `GOG_HOME`, keyring files, or refresh tokens between agents.

## Canary Tests

Marsha passes only when both routes independently prove:

- `gog auth list --check` and `gog auth doctor --check` succeed.
- The returned account identity exactly matches the intended alias.
- `main-google` can read and modify one approved Drive canary, and read/send one controlled message from Jack's Gmail.
- `agent-google` can read and modify one canary in its own Drive, and read/send one controlled message from its own Gmail.
- Calendar, Contacts, Tasks, Docs, Sheets, and other enabled services pass one harmless read test; use a reversible canary write where the service supports writing.
- OpenClaw logs identify Marsha as the acting agent.
- Google activity/audit evidence shows the correct Google identity.
- No unintended file, email, event, contact, task, permission, or external recipient changes.
- Revoking one account breaks only that alias; reauthorization restores only that alias.
- Photo Picker, Admin, Groups, and Keep are reported separately and are not falsely marked complete.

## Fleet Rollout

After the canary and Production OAuth design pass:

- Repair and reverify the VPS2 config blocker before authorizing Harry, Frank, or Suzy.
- Authorize one agent at a time.
- Give each agent its own encrypted token store and both aliases.
- Require the identity, read, reversible-write, audit, and revocation checks for both accounts.
- Stop on the first unexpected account, scope, visibility, mutation, API error, or audit result.
- Recreate VPS1 containers only through `/opt/openclaw/agents/{agent}/op-start-{agent}.sh` or the equivalent 1Password-aware startup route.

## Ruby On VPS3

Ruby is Hermes, not OpenClaw GOG. Her installed skill currently uses one token file at `/opt/data/google_token.json`.

- Do not overwrite one identity with the other.
- First inspect the live Hermes skill and setup help for supported multi-account storage.
- If it cannot isolate two tokens, keep `jack@zbiz.work` in the native Google Workspace route and configure the individual Gmail through a separate approved mail/Google route.
- Test both identities independently against the same completion standard.
- Record Ruby's exact routing in GitHub before declaring her complete.

## Failure And Revocation

If the wrong account, unexpected data, blocked scope, or excessive capability appears:

- Stop immediately.
- Revoke the affected token in GOG and Google Account/Workspace security controls.
- Preserve the other account's token until its isolation is verified.
- Record the exact account, requested scope, observed result, and decision required.
- Return to Diagnose -> Solution -> Confirmation -> Act for any new material risk.

For GOG, confirm live help before removal, then use the exact email:

```bash
gog auth remove jack@zbiz.work
gog auth remove agent-address@gmail.com
```

## Completion Standard

The rollout is complete only when:

- Both identities are authorized for every intended agent.
- Maximum available GOG user scopes are confirmed from the live client.
- Both aliases are explicit and independently verified.
- Supported read/write canaries pass without unintended changes.
- Read-only-only services are accurately recorded as such.
- Admin, Groups, Keep, and Photo Picker are not falsely included.
- Revocation isolation passes.
- Google and agent-level audit evidence is saved without secrets.
- Every agent has an independent completion record.
- No credential or authorization artifact appears in GitHub, Notion, chat, logs, or memory.

## Sources

- Official GOG documentation: https://github.com/openclaw/gogcli/blob/main/README.md
- Google installed-app OAuth documentation: https://developers.google.com/identity/protocols/oauth2/native-app
- Fleet activation record: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/ai-agent-sops/zedbiz-main-vps/tracking/2026-08-28-google-drive-gog-fleet-activation.md
- Tracking issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/87
