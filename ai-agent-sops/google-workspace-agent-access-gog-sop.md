# Google Workspace Agent Access — GOG SOP

Date: 2026-09-01 | Agent: Cody | Status: Active

## Purpose

Connect ZedBiz agents to an approved Google Workspace Drive in a controlled, testable way. This SOP is the technical source of truth for authorization, canary testing, fleet rollout, verification, revocation, and failure handling.

## Decision

- Create `agents@zbiz.work` as a paid, non-admin Google Workspace user because production agents require read/write access.
- Give that identity Contributor access only to the approved Shared Drives. Contributor supports reading, creating, uploading, and editing without Shared Drive membership administration or trash authority.
- Use GOG for OpenClaw agents on VPS1, VPS2, and VPS4.
- Use Ruby's native Hermes `google-workspace` skill on VPS3.
- Start the canary with Drive-only, read-only OAuth to prove identity and boundaries.
- After the read-only canary passes, promote `agents@zbiz.work` to Contributor and reauthorize the canary with Drive full scope for a controlled write test.
- Roll out only after approved-file read, out-of-scope denial, create/upload, edit/read-back, audit-log, and revocation checks pass.
- Do not connect `jack@zbiz.work` as the agent OAuth identity.
- Do not use the Codex Google Drive connector as the credential route for persistent OpenClaw agents.
- Do not use rclone or domain-wide delegation for the first implementation. Reserve rclone for approved bulk sync/backup and domain-wide delegation for a separately reviewed administrator use case.

## Current Fleet State

Live read-only verification completed 2026-09-01 at approximately 22:38 Mountain Time:

- VPS1: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma are running, healthy, at zero restarts, and using GOG v0.38.1. The GOG skill is eligible and model-visible on all eleven. Every account check returned `No tokens stored`.
- VPS2: Harry, Frank, and Suzy services are active and each runs GOG v0.38.1. Every account check returned `No tokens stored`. The current OpenClaw CLI cannot complete the GOG skill-info check because each config contains the unrecognized key `meta.lastTouchedAt`; skill visibility must be repaired and reverified before authorization.
- VPS3: the `hermes-ruby` container is running. Ruby's Hermes `google-workspace` skill v1.2.0 is present inside the active container. Its live check reports `NOT_AUTHENTICATED: No token at /opt/data/google_token.json`.
- VPS4: Rocky's OpenClaw gateway is active. GOG v0.38.1 is eligible and model-visible. The account check returned `No tokens stored`.
- No audited agent is authenticated to Google.
- No live Google Drive search or known-file read has passed.
- Recheck `gog --version`, live help, skill visibility, and authentication state immediately before authorization.
## Confirmed ZedBiz Workspace And Shared Drives

Jack confirmed the Google Workspace domain is `zbiz.work` and the current administrator/source account is `jack@zbiz.work`.

The Shared Drives visible in the supplied Google Drive screenshot are:

- `Z-Administrative`
- `Z-Clients`
- `Z-Core-Ventures`
- `Z-External`
- `Z-Marketing`
- `z-migration`
- `Z-Operations`
- `Z-Prospects`
- `Z-Ventures`

Shared Drives belong to the Workspace organization; `jack@zbiz.work` is the account currently used to view and administer them.

### Licence Decision

- Jack confirmed the agents require read/write access.
- Use a paid Google Workspace licence for `agents@zbiz.work`.
- Cloud Identity Free is not the production choice because internal Shared Drive membership is limited to Viewer.
- An alias or Google Group is not an OAuth identity and cannot replace the licensed account.
- One paid shared identity is sufficient when all authorized agents have the same Drive boundary. Google audit logs will identify `agents@zbiz.work`; per-agent attribution must come from OpenClaw execution records.
- If selected agents need different Drive boundaries or independent Google audit attribution, create separate licensed identities for those write-capable roles.

### Authentication Boundary

- Use `jack@zbiz.work` to create/manage the dedicated agent identity and grant Shared Drive membership.
- Use a dedicated non-admin identity such as `agents@zbiz.work` for agent OAuth.
- Add `agents@zbiz.work` as Viewer for the security canary, then Contributor on the Shared Drives approved for production read/write access.
- Google Drive read-only OAuth follows all files the authenticated identity can already access; it does not restrict access to a chosen list of Shared Drives.
- Authorizing `jack@zbiz.work` would therefore expose its My Drive and every Shared Drive/file available to that account. Do not use it as the default agent OAuth identity unless Jack explicitly accepts that full visibility.
- If different agents require different Drive boundaries or write attribution, use separate Workspace identities or groups rather than one shared token boundary.

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
- Moving files to Trash, permanent deletion, Shared Drive membership changes, broad permission changes, or structural reorganization.
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

Create `agents@zbiz.work` as a paid, regular, non-admin Google Workspace user.

- Assign one paid Workspace licence with Drive support.
- Use a ZedBiz-controlled password and MFA/passkey stored through the approved 1Password process.
- Do not grant admin roles.
- Do not add broad groups that expose unrelated Drives.
- Record only the non-secret account name, owner, approved folder/Shared Drive, role, and review date.

### Drive Boundary

Create or select a dedicated Shared Drive or folder, such as `ZedBiz Agent Approved Files`.

- Put only approved, non-secret files inside.
- Grant the automation identity Viewer access for the security canary, then Contributor for approved production read/write access.
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
gog auth add agents@zbiz.work \
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
export GOG_ACCOUNT='agents@zbiz.work'
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

## Production Read/Write Rollout

Read/write access is an approved business requirement. Preserve the read-only canary as the first security gate, then expand deliberately.

### Promote The Canary

- Assign the paid Workspace licence to `agents@zbiz.work`.
- Promote its membership from Viewer to Contributor only on the approved Shared Drives.
- Confirm the live GOG v0.38.1 contract with `gog auth add --help`.
- Reauthorize the canary:

```bash
gog auth add agents@zbiz.work \
  --services drive \
  --drive-scope full \
  --manual \
  --force-consent
```

- Do not apply the runtime `--readonly` flag when performing the approved write test.
- Use exact command allowlists, `--no-input`, dry-run support where available, and explicit confirmation gates for destructive or sharing operations.

### Controlled Write Test

- Create or upload one clearly named canary file in an approved test folder.
- Read the file back and verify its content.
- Edit or replace only that canary and verify the expected result.
- Confirm Google audit logs identify `agents@zbiz.work`.
- Confirm the out-of-scope canary remains inaccessible.
- Leave trash/delete, permission management, external sharing, and Shared Drive membership commands disabled.
- Revoke the canary token and prove access fails, then reauthorize for production only after the revocation test passes.

### Fleet Rollout

- Authorize one agent at a time with a separate encrypted token store.
- Require the approved read and controlled write tests for every agent.
- Record the OpenClaw agent name, token creation date, approved Shared Drives, test file, audit evidence, and revocation result.
- Stop on the first unexpected account, scope, visibility, mutation, or audit result.

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
gog auth remove agents@zbiz.work
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
