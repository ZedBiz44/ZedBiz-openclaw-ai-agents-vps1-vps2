# Google Workspace Agent Access — GOG SOP

Date: 2026-09-01 | Agent: Cody | Status: Active

## Purpose

Connect ZedBiz agents to an approved Google Workspace Drive in a controlled, testable way. This SOP is the technical source of truth for authorization, canary testing, fleet rollout, verification, revocation, and failure handling.

## Decision

- Use a dedicated, non-admin Google Workspace automation user controlled by ZedBiz.
- Give that identity Viewer access only to a dedicated Shared Drive or approved folder.
- Use GOG for OpenClaw agents on VPS1, VPS2, and VPS4.
- Use Ruby's native Hermes `google-workspace` skill on VPS3.
- Start with Drive-only, read-only OAuth and one canary agent.
- Roll out only after the canary can read an approved file and cannot see an out-of-scope file.
- Do not connect Jack's personal Google account.
- Do not use the Codex Google Drive connector as the credential route for persistent OpenClaw agents.
- Do not use rclone or domain-wide delegation for the first implementation. Reserve rclone for approved bulk sync/backup and domain-wide delegation for a separately reviewed administrator use case.

## Current Fleet State

- VPS1's eleven OpenClaw agents were verified on 2026-09-01 with GOG v0.38.1 after the fleet update.
- VPS2's Harry, Frank, and Suzy and VPS4's Rocky were last verified on 2026-08-28 with GOG v0.34.1.
- On every verified OpenClaw runtime, GOG is installed, enabled, eligible, and model-visible, with a separate persistent state directory and encrypted file-keyring route.
- Recheck `gog --version` and live help before authorization; the installed version, not an old planning page, controls the command contract.
- Ruby has the Hermes `google-workspace` skill v1.2.0.
- No Google account is authenticated and no known-file Drive test has passed yet.
- Software readiness is not account access.

## Scope

### Included

- Google Drive search, metadata, file listing, download/export, and read-only access.
- One dedicated Workspace automation identity.
- One approved Shared Drive or folder.
- A protected Desktop OAuth client.
- Separate per-agent token stores.
- Canary-first rollout and revocation testing.

### Excluded Until Separately Approved

- Gmail, Calendar, Contacts, Admin SDK, Chat, YouTube, and other Google services.
- File creation, upload, rename, move, sharing changes, permission changes, or trash/delete.
- Jack's personal My Drive.
- Domain-wide delegation.
- Public links or external sharing.
- Copying OAuth JSON, refresh tokens, service-account keys, passwords, or recovery codes into Notion, GitHub, chat, agent memory, logs, or ordinary configuration files.

## Roles

### Human — Jack or Google Workspace Administrator

- Select or create the dedicated automation identity.
- Choose the exact Shared Drive or folder.
- Configure Google Cloud and Google Workspace.
- Review the account shown on Google's consent screen.
- Approve the Drive-only read-only consent.
- Approve any future permission or scope expansion.

### AI Agent — Cody or Authorized Infrastructure Agent

- Verify installed client and skill visibility.
- Import the OAuth client through a protected temporary path.
- Generate the headless authorization URL.
- Pause for the human consent step.
- Store tokens only in the agent-specific protected GOG or Hermes store.
- Run boundary, read, audit, and revocation tests.
- Stop on unexpected scope, account, visibility, or runtime behavior.

## Required Google Setup

### Dedicated Workspace Identity

Create a regular, non-admin user such as `agents@<zedbiz-domain>`.

- Use a ZedBiz-controlled password and MFA/passkey stored through the approved 1Password process.
- Do not grant admin roles.
- Do not add broad groups that expose unrelated Drives.
- Record only the non-secret account name, owner, approved folder/Shared Drive, role, and review date.

### Drive Boundary

Create or select a dedicated Shared Drive or folder, such as `ZedBiz Agent Approved Files`.

- Put only approved, non-secret files inside.
- Grant the automation identity Viewer access.
- Create one approved canary file inside the boundary.
- Create or identify one out-of-scope canary elsewhere that the identity must not see.
- Confirm external sharing is restricted by policy.

### Google Cloud Project

- Create or select a ZedBiz-controlled Google Cloud project.
- Enable the Google Drive API.
- Configure the OAuth consent screen as Internal when the automation account belongs to the Workspace organization.
- Create an OAuth client with application type Desktop app.
- Download the client JSON once and store it as a secure document in 1Password.
- Delete the unprotected browser download after the protected copy is verified.
- Do not create an API key; Google Drive user access uses OAuth.

## OpenClaw GOG Canary

Use Amanda as the first OpenClaw canary unless Jack selects another agent.

### Preflight

Inside the canary's normal protected runtime:

```bash
gog --version
openclaw skills info gog --json
gog auth list --check
gog auth add --help
```

Pass conditions:

- Expected GOG version is available.
- The GOG skill reports `eligible: true` and `modelVisible: true`.
- The agent has its own persistent `GOG_HOME`.
- No account is unexpectedly present.
- The installed help confirms the authorization flags before execution.

### Import OAuth Client

Expose the Desktop OAuth JSON through a temporary protected 1Password injection path, then run:

```bash
gog auth credentials set /secure/temporary/client_secret.json
gog auth credentials list
```

- Never print the JSON.
- Remove the temporary file or mount after the client is imported.
- Do not copy another agent's token store.

### Human Authorization Gate

Run:

```bash
gog auth add agents@<zedbiz-domain> \
  --services drive \
  --drive-scope readonly \
  --manual
```

- The agent sends Jack only the Google authorization URL.
- Jack opens it in a trusted browser signed in as the dedicated automation user.
- Jack verifies the displayed email and that only Drive read access is requested.
- Jack approves consent and returns the full redirected loopback URL through the approved temporary authorization channel.
- Treat the returned URL/code as sensitive until exchanged.
- The agent completes the exchange and does not store the URL/code in Notion, GitHub, logs, or memory.

### Verify Identity and Read Boundary

```bash
export GOG_ACCOUNT='agents@<zedbiz-domain>'
gog auth list --check
gog auth doctor --check
gog --account "$GOG_ACCOUNT" --readonly --no-input --wrap-untrusted --json drive search "OpenClaw Drive Pilot Canary"
```

The canary passes only when:

- The authenticated email is the dedicated automation identity.
- The approved canary file is found.
- Its metadata and supported content can be read without editing.
- The out-of-scope canary cannot be found or opened.
- Jack's personal My Drive and unrelated Shared Drives are not visible.
- Google audit logs show the expected identity and activity.
- No write-capable Drive scope was granted.

## Fleet Rollout

After the canary passes:

- Authorize one agent at a time.
- Use the same approved OAuth client and Workspace identity only when every agent has the identical read boundary and individual Google audit attribution is not required.
- Keep a separate encrypted token store for every agent.
- Never clone `GOG_HOME`, keyring files, or refresh tokens between agents.
- Verify each agent independently with `gog auth list --check`, `gog auth doctor --check`, and the known-file boundary test.
- Stop the rollout on the first unexpected scope, account, file visibility, token, or audit result.
- Recreate VPS1 containers only through `/opt/openclaw/agents/{agent}/op-start-{agent}.sh` or the equivalent 1Password-aware startup route. Bare `docker compose` bypasses protected secret resolution.

## Ruby on VPS3

Ruby does not use GOG. Use the installed Hermes skill:

```bash
python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check
python /opt/data/skills/productivity/google-workspace/scripts/setup.py \
  --client-secret /secure/temporary/client_secret.json
python /opt/data/skills/productivity/google-workspace/scripts/setup.py \
  --auth-url --services drive --format json
```

- Jack opens the returned authorization URL as the same dedicated automation identity.
- Jack verifies Drive-only permissions and returns the redirected URL/code through the approved temporary channel.
- Complete the exchange:

```bash
python /opt/data/skills/productivity/google-workspace/scripts/setup.py \
  --auth-code "FULL_REDIRECT_URL_OR_CODE" --format json
python /opt/data/skills/productivity/google-workspace/scripts/setup.py --check
```

- Remove the temporary client JSON.
- Run the same approved-file and out-of-scope boundary tests.
- Treat Ruby's token store as separate from all GOG stores.

## Write Access — Separate Change

Do not add write access during the read-only rollout.

If a role later needs file creation, upload, rename, move, or trash:

- Document the exact business need and target folder.
- Approve only the selected agent and folder.
- Prefer `--drive-scope file` where it fits; otherwise explicitly approve full Drive scope.
- Reauthorize the selected account.
- Create one clearly named test file, read it back, check audit logs, and move it to trash.
- Confirm out-of-scope locations remain inaccessible.
- Use individual Workspace identities for write-capable agents when attribution matters.

## Failure Handling

### Wrong Account or Excess Visibility

- Stop immediately.
- Revoke the token.
- Remove Drive/Shared Drive membership.
- Inspect group membership and inherited permissions.
- Redesign the boundary before retrying.

### Authorization Denied or App Blocked

- Confirm the automation identity belongs to the Workspace organization.
- Confirm the consent screen is Internal or the user is an authorized test user.
- Confirm Google Admin app-access controls permit the OAuth client and requested Drive scope.
- Confirm Drive API is enabled.
- Do not add broader scopes as a troubleshooting shortcut.

### Token Exists but Drive Fails

- Run `gog auth doctor --check`.
- Confirm the selected account, OAuth client, and agent-specific state path.
- Confirm the account still has access to the exact Shared Drive/folder.
- Confirm installed command syntax with `gog auth add --help` and `gog schema --json`.
- Reauthorize only after current scopes and revocation state are understood.

### Revocation and Rollback

For GOG:

```bash
gog auth remove agents@<zedbiz-domain>
```

For Ruby, use the installed Hermes setup script's revoke operation after confirming its live help.

Also:

- Revoke the app/token in Google Account or Google Admin security controls.
- Remove the identity from the Shared Drive/folder.
- Suspend the identity if compromise is suspected.
- Verify the former token can no longer list or read the canary file.
- Record only non-secret revocation evidence.

## Completion Standard

Google Drive access is complete only when:

- The correct dedicated account is authenticated.
- The client and skill are visible in the intended runtime.
- Drive-only read-only scope is confirmed.
- The approved canary can be read.
- The out-of-scope canary is inaccessible.
- Google audit logs show expected activity.
- Revocation has been tested on the canary before fleet rollout.
- Every authorized agent has an independent verification record.
- No secret appears in Notion, GitHub, chat, logs, or agent memory.

## Sources

- Official GOG documentation: https://github.com/openclaw/gogcli/blob/main/README.md
- Google installed-app OAuth documentation: https://developers.google.com/identity/protocols/oauth2/native-app
- Fleet activation record: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/ai-agent-sops/zedbiz-main-vps/tracking/2026-08-28-google-drive-gog-fleet-activation.md
- Tracking issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/87
