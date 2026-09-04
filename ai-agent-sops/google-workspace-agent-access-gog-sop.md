# Google Workspace Agent Access — GOG and IMAP SOP

Date: 2026-09-04 | Agent: Cody | Status: Active

## Purpose

Connect every ZedBiz OpenClaw agent to the shared Google Workspace account through GOG, give each agent a professional `name@zbiz.work` email alias, and route new alias mail to the correct agent through OpenClaw's bundled IMAP trigger.

This is the single operating source for the Google account model, rollout order, human approvals, testing, security boundaries, and completion standard. VPS-specific Notion pages only summarize the local connection and link back here.

## Start Here — Final Design

- `jack@zbiz.work` is the only paid Google Workspace user and the only Google account used for this shared GOG rollout.
- Every OpenClaw agent gets its own Workspace email alias, such as `marsha@zbiz.work`.
- An alias is not a Google account. It has no password, separate inbox, Drive, Calendar, or OAuth login.
- All alias mail arrives in the single `jack@zbiz.work` Gmail mailbox.
- Gmail filters apply one agent-specific label to each alias.
- Each OpenClaw instance uses the bundled IMAP trigger to watch only its assigned Gmail label and start a restricted mail-reader session for approved new mail.
- GOG gives the agent access to `jack@zbiz.work` for Drive, Gmail, Calendar, Docs, Sheets, and other supported Google services.
- GOG's automatic Gmail Pub/Sub watcher will not process the same messages as IMAP. Use one inbound trigger route per message.
- Ruby on VPS3 is Hermes and is outside this OpenClaw procedure.
- Any separately created consumer Gmail accounts are outside this shared-alias rollout. They are not required for the selected design and must not be confused with Workspace aliases.

## Follow-Along Setup Roadmap

This is the ordered checklist Jack can follow while Cody performs as much of the work as the available access allows.

### Step 1 — Confirm The Agent Alias List

**Cody prepares and checks:**

- Amanda: `amanda@zbiz.work`
- Edith: `edith@zbiz.work`
- Gohzed: `gohzed@zbiz.work`
- Grogar: `grogar@zbiz.work`
- Inga: `inga@zbiz.work`
- Maggie: `maggie@zbiz.work`
- Marsha: `marsha@zbiz.work`
- Terry: `terry@zbiz.work`
- Victor: `victor@zbiz.work`
- Vivian: `vivian@zbiz.work`
- Wilma: `wilma@zbiz.work`
- Frank: `frank@zbiz.work`
- Harry: `harry@zbiz.work`
- Suzy: `suzy@zbiz.work`
- Rocky: `rocky@zbiz.work`

**Jack approves:**

- The spelling of every alias.
- That none of these addresses must become a separate paid Workspace user.

Google currently allows up to 30 aliases on one Workspace user at no extra cost, so this 15-alias plan fits within the current limit. Recheck the limit before future expansion.

### Step 2 — Create The Workspace Aliases

**Cody can perform the screen work when an authorized Google Admin browser session is available. Jack must:**

- Sign in as the Workspace administrator.
- Complete two-step verification.
- Approve any account-security prompt.

Create every approved alias on the existing `jack@zbiz.work` user. Do not create additional paid users. Confirm each alias appears in Google Admin before continuing.

### Step 3 — Create Gmail Labels And Sorting Rules

**Cody creates:**

- One Gmail label per agent.
- One Gmail filter per alias that applies the matching label.
- A clear naming pattern that prevents two agents from sharing the same label.

Send one harmless test email to each alias. Confirm that it reaches Jack's mailbox and receives only the correct agent label.

### Step 4 — Prepare The Google Cloud OAuth Project

**Cody prepares the project. Jack handles private sign-in and approval screens.**

- Use one ZedBiz-controlled Google Cloud project owned by `jack@zbiz.work`.
- Enable the APIs required by the selected GOG services.
- Configure the OAuth audience as **Internal** because the selected GOG account is the Workspace user `jack@zbiz.work`.
- Create a Desktop app OAuth client.
- Store the downloaded client JSON in the approved 1Password item.
- Remove any ordinary unprotected download after the protected copy is verified.

If a consumer Gmail account is later added, stop and review the OAuth audience and publication requirements before authorizing it.

### Step 5 — Prepare Protected Per-Agent Credentials

**Cody prepares:**

- A separate encrypted GOG token store for every agent.
- A separate protected IMAP secret reference for every agent where Google's current authentication method permits it.
- Clear account naming: `main-google` always means `jack@zbiz.work`.

Never copy a completed token store between agents. Never place OAuth JSON, refresh tokens, app passwords, authorization codes, recovery codes, or complete configuration files in Notion, GitHub, chat, logs, or agent memory.

### Step 6 — Connect Marsha To GOG First

Marsha is the first test agent.

**Cody:**

- Confirms the live GOG version and skill visibility.
- Imports the protected Desktop OAuth client into Marsha's isolated GOG store.
- Starts authorization for `jack@zbiz.work` with maximum normal user access, full Drive scope, and full Gmail scope.
- Assigns the `main-google` alias.
- Pauses for Jack at Google's consent screen.

**Jack:**

- Opens the authorization link in a trusted browser.
- Confirms the displayed account is exactly `jack@zbiz.work`.
- Reviews and approves the requested Google permissions.
- Completes any two-step verification.
- Returns only the temporary redirect result through the approved protected channel.

### Step 7 — Connect Marsha's Alias To IMAP

**Cody:**

- Enables OpenClaw's bundled IMAP trigger in Marsha's runtime.
- Uses the protected `jack@zbiz.work` mailbox credential.
- Points the watched mailbox to Marsha's Gmail label as exposed through IMAP.
- Routes accepted messages to a restricted mail-reader agent.
- Limits accepted senders and requires verified sender authentication.
- Keeps delivery, file, browser, runtime, gateway, automation, and unrelated tools disabled in the mail-reader session.

The label is a routing rule, not a security wall. The underlying mailbox credential can access Jack's mailbox and must be protected accordingly.

### Step 8 — Run The Marsha Tests

Marsha passes only when:

- GOG proves the authenticated account is `jack@zbiz.work`.
- GOG can read and make one reversible change to the approved Drive test item.
- GOG can search/read controlled Gmail and complete one approved draft/send test.
- A new message to `marsha@zbiz.work` receives the Marsha label.
- Only Marsha's IMAP route starts.
- A message for another alias does not start Marsha.
- Messages already present before monitoring are not treated as new triggers.
- OpenClaw's IMAP route does not send or modify mail.
- The same message is not also processed by a GOG Pub/Sub watcher.
- Restart persistence and revocation are proven.
- Google records `jack@zbiz.work`; OpenClaw records Marsha as the acting agent.
- No unintended file, email, label, event, permission, or recipient changes.

### Step 9 — Roll Out One Agent At A Time

After Jack accepts Marsha's test:

- Roll through VPS1 agents one at a time.
- Repair and reverify the known VPS2 configuration problem before connecting Frank, Harry, or Suzy.
- Connect Rocky on VPS4 after the same preflight.
- Give every agent its own GOG token store, IMAP secret reference, Gmail label, filter, and verification record.
- Stop on the first wrong account, wrong label, duplicate processing, unexpected visibility, failed restart, or unplanned change.

### Step 10 — Add Sending From Agent Aliases Only If Needed

The IMAP trigger receives mail but does not send replies.

- GOG can send through the authenticated `jack@zbiz.work` Gmail account.
- Sending visibly from `name@zbiz.work` requires that alias to be configured and tested as a Gmail send-as identity.
- Keep outbound alias sending separate from the inbound IMAP test.
- Jack must approve the sending policy and the first external send for each use case.

## What GOG Access Includes

The selected authorization for `jack@zbiz.work` is maximum normal user OAuth:

```bash
gog auth add jack@zbiz.work \
  --services all-user \
  --drive-scope full \
  --gmail-scope full \
  --manual \
  --force-consent

gog auth alias set main-google jack@zbiz.work
```

`all-user` covers the supported user-facing Google catalogue available to the installed GOG version. Some services are read-only by Google's design, and OAuth does not create product entitlements or data that the account does not have.

Google Admin SDK, Cloud Identity Groups, and Keep require service-account domain-wide delegation and are outside this user-OAuth rollout. Photo Picker remains a separate opt-in.

## Google Workspace And Drive Boundary

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

OAuth cannot limit `jack@zbiz.work` to selected Shared Drives. Every authorized agent can potentially access Jack's Gmail, My Drive, calendars, contacts, tasks, files, and every Shared Drive item visible to Jack.

Google will show `jack@zbiz.work` in its activity and audit records. Per-agent attribution must come from isolated token stores and OpenClaw execution records.

## GOG And IMAP Have Different Jobs

### GOG

Use GOG when an agent deliberately needs to:

- Search or read Gmail.
- Create a draft, send, or reply after the required approval.
- Work with Drive, Docs, Sheets, Slides, Calendar, Contacts, Tasks, and other supported Google services.
- Perform an account-specific, auditable command.

### OpenClaw IMAP Trigger

Use IMAP when:

- A new allowed email arrives for an agent alias.
- That arrival should immediately start a restricted reader session.
- No public webhook is wanted.

The bundled IMAP trigger does not send, reply, change message flags, or backfill old mail.

### Do Not Double-Trigger

Do not enable both OpenClaw IMAP and GOG Gmail Pub/Sub watch for the same mailbox labels and messages. GOG's normal search/read/send tools may remain available on demand.

## Human Approval And Safety Rules

Maximum Google permission is capability, not blanket authority. Agents still need Jack's approval before:

- Sending consequential external communications.
- Deleting, trashing, moving, or broadly reorganizing data.
- Changing permissions, Shared Drive membership, external sharing, or public links.
- Creating, changing, or cancelling meetings with outside attendees.
- Publishing Apps Script changes or changing Ads.
- Making financially, legally, or reputationally consequential changes.

Jack must personally handle Google sign-in, two-step verification, OAuth consent, and any prompt requesting a password or recovery method. Never send a Google password in chat.

## VPS Connection Pages

These pages contain only host-specific connection summaries and point back to this SOP:

- VPS1 Google Workspace, GOG, and IMAP Connection.
- VPS2 Google Workspace, GOG, and IMAP Connection.
- Rocky Google Workspace, GOG, and IMAP Connection — VPS4.

Do not copy the full authorization procedure into VPS setup pages.

## Failure And Revocation

Stop immediately if the wrong Google account, wrong label, unexpected mail, duplicate trigger, excessive visibility, blocked scope, or unplanned change appears.

- Revoke the affected GOG token.
- Remove or disable the affected IMAP secret reference.
- Disable the affected Gmail filter or alias when necessary.
- Preserve the other agents' credentials until isolation is verified.
- Record what happened without recording secret values.
- Return to Diagnose -> Solution -> Confirmation -> Act when a new material risk appears.

## Completion Standard

The rollout is complete only when:

- The approved aliases exist on `jack@zbiz.work`.
- Every alias routes to exactly one tested Gmail label.
- Every OpenClaw agent has an isolated GOG store authorized as `jack@zbiz.work`.
- Every OpenClaw agent watches only its assigned IMAP mailbox/label.
- GOG read/write tests and IMAP new-message tests pass.
- Duplicate GOG/IMAP triggering is prevented.
- Restart persistence and revocation are proven.
- Google and OpenClaw records identify the account and acting agent without exposing secrets.
- Every agent has an independent completion record.
- Any untested feature remains marked pending.

## Sources

- Main Notion SOP: https://app.notion.com/p/3cfa3e33d5818176ab4ee0922cc85c50
- Official GOG documentation: https://github.com/openclaw/gogcli/blob/main/README.md
- Official GOG Gmail watch documentation: https://github.com/openclaw/gogcli/blob/main/docs/watch.md
- Official OpenClaw IMAP documentation: https://docs.openclaw.ai/automation/imap
- Google Workspace alias documentation: https://support.google.com/a/answer/33327
- Google installed-app OAuth documentation: https://developers.google.com/identity/protocols/oauth2/native-app
- Fleet activation record: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/blob/main/ai-agent-sops/zedbiz-main-vps/tracking/2026-08-28-google-drive-gog-fleet-activation.md
- Tracking issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/87
