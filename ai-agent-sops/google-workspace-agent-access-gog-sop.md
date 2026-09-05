# Google Workspace Agent Access Through GOG SOP

Date: 2026-09-05 | Agent: Documentation maintainer | Status: Active

## Purpose

This SOP explains how to connect approved AI agents to the ZedBiz Google Workspace account through GOG and give each agent its approved Gmail alias.

It is written to stay useful when agents, servers, or test groups change. Current names, rollout groups, host paths, and test results belong in the linked GitHub issue and separate rollout records.

IMAP and automatic Gmail watching are not part of this setup.

## What We Are Building

- One paid Google Workspace user: `jack@zbiz.work`.
- One approved Gmail alias for each selected agent, using the pattern `{agent-name}@zbiz.work`.
- One Gmail owner label for each selected agent, using the pattern `Agent/{AgentName}`.
- A small shared set of status labels.
- One isolated GOG credential store for each agent.
- Maximum normal user access through GOG for the approved Google services.
- One outside Gmail profile per agent.
- The reusable `z-gmail-gog` Skill in every approved agent workspace.
- `draft_only` or `send_allowed` mode chosen separately for each agent.

An alias is an extra address on the shared account. It is not a separate Google user, password, inbox, Drive, Calendar, or OAuth login. Mail sent to an alias arrives in the `jack@zbiz.work` Gmail mailbox.

## Who Does What

| Role | Responsibility |
|---|---|
| Authorized human approver | Approves aliases, completes private Google sign-in and consent, chooses each agent's sending mode, and accepts test results. |
| Google Workspace administrator | Creates aliases and checks the Google account settings. |
| Implementation operator | Creates labels and filters, prepares GOG, installs profiles and the skill, runs tests, and records proof. |
| AI agent | Uses only its assigned alias and label and follows its active profile and skill. |

One person may hold more than one role. Current people and agent names are recorded outside this evergreen SOP.

## Ordered Setup Checklist

### Step 1 — Record The Approved Rollout Group

In the tracking issue, record every selected agent, approved alias, platform and host, expected workspace and GOG credential-store location, and starting email mode.

Do not hard-code the current roster into this SOP.

### Step 2 — Create Every Approved Gmail Alias

In Google Admin, add each approved `{agent-name}@zbiz.work` alias to the existing `jack@zbiz.work` user.

- Do not create another paid user unless separately approved.
- Inspect the existing aliases first and create only missing ones.
- Confirm every saved alias appears on the correct Workspace user.
- Record the completed alias list in the rollout issue.

### Step 3 — Create The Gmail Labels

Create one owner label for each selected agent:

- `Agent/{AgentName}`

Create these shared status labels once:

- `Status/Needs-Reply`
- `Status/Waiting-On-Them`
- `Status/Waiting-On-Approver`
- `Status/Done`
- `Status/Noise`

These are Gmail labels—the folders shown beside messages in Gmail. They are not printed labels and are not security walls.

### Step 4 — Create One Sorting Filter Per Alias

For each alias, create a Gmail filter that matches mail addressed to that exact alias and applies only the matching `Agent/{AgentName}` label.

The filter must not delete, archive, forward, mark read, or change unrelated mail unless a later approved rule says so.

Send one harmless test message to every alias. Confirm the message reaches the shared mailbox and receives the correct owner label.

### Step 5 — Prepare Google OAuth

Use the approved ZedBiz Google Cloud project and Desktop OAuth client.

- Enable the APIs required by the installed GOG version.
- Use the Workspace-controlled OAuth audience approved for `jack@zbiz.work`.
- Store the OAuth client securely.
- Never put the client secret, authorization code, refresh token, recovery code, password, or full credential file in GitHub, Notion, chat, logs, or agent memory.
- Stop if Google asks for billing, a paid service, another paid user, or an unexpected account.

### Step 6 — Prepare One Isolated GOG Store Per Agent

Each agent must have its own encrypted GOG credential store.

- Never copy a completed token store from one agent to another.
- Use the account alias `main-google` for `jack@zbiz.work`.
- Confirm the actual runtime path before changing anything.
- Preserve unrelated credentials and configuration.

The approved authorization shape is:

```bash
gog auth add jack@zbiz.work \
  --services all-user \
  --drive-scope full \
  --gmail-scope full \
  --manual \
  --force-consent

gog auth alias set main-google jack@zbiz.work
```

Confirm these flags against the installed GOG version before running them.

### Step 7 — Complete Private Google Consent

For each isolated agent store:

- The implementation operator starts authorization.
- The authorized human approver opens the Google link in a trusted browser.
- Confirm the displayed account is exactly `jack@zbiz.work`.
- Review and approve the requested permissions.
- Complete password and two-step verification privately.
- Return only the temporary authorization result through the approved protected route.

Never ask anyone to paste a Google password or two-factor code into chat.

### Step 8 — Create The Outside Agent Profile

Create a profile outside the reusable skill package for each agent. It must contain the agent display name, sender alias, owner label, email mode, normal email responsibilities, human approval contact or role, and stop rules.

The YAML profile is strong operating guidance, but it is not the technical send lock. GOG permissions enforce whether sending is possible.

### Step 9 — Configure Sending From The Correct Alias

Confirm the alias is available as a Gmail sending identity for the shared account. Then configure the agent and GOG command to use the profile's exact sender alias.

- Drafts and sent messages must use the assigned alias.
- Never silently fall back to `jack@zbiz.work` or another agent's alias.
- If the requested alias is unavailable or rejected, stop and report the problem.
- GOG may help select the addressed alias, but profile guidance alone cannot guarantee the sender identity. Real send testing is required.

### Step 10 — Install The Gmail Skill

Install the validated `z-gmail-gog` package in each approved agent workspace only after that agent has a working isolated GOG connection, confirmed outside profile, confirmed owner label and alias, recorded sending mode, and known rollback method.

Start a fresh agent session and confirm the skill loads.

### Step 11 — Test One Agent First

Use one selected agent as the first live test. The selected name belongs in the tracking issue, not in this SOP.

The first agent must prove:

- GOG identifies the account as `jack@zbiz.work`.
- The isolated credential store survives a restart.
- Gmail search and read work.
- The agent sees and uses only its assigned owner label during the test.
- A draft uses the correct alias.
- `draft_only` mode technically blocks sending when selected.
- `send_allowed` mode sends one harmless approved message from the correct alias when selected.
- A different agent's alias is not used.
- The agent stops for money, legal, security, sensitive, angry-client, unapproved-price, and unclear requests.
- Revocation or removal works.
- No unrelated email, file, event, permission, label, or recipient changes.

Stop and diagnose any failure before rolling the same setup to the remaining group.

### Step 12 — Roll Out To The Remaining Approved Agents

After the first agent passes:

- Repeat the same isolated setup for every agent in the approved rollout group.
- Test each alias, owner label, profile, credential store, Gmail read, draft, send mode, restart, and rollback.
- Record proof separately for every agent.
- Do not mark the group complete because only one agent worked.

## How Agents Use Gmail

GOG lets an authorized agent deliberately search, read, label, draft, reply, and—when technically allowed—send Gmail messages in the shared account.

The owner label tells the agent which mail it is responsible for. The outside profile tells it which alias to use and what it may do. The skill explains the safe working process. GOG provides the actual Google access and the technical send capability.

There is no automatic inbox watcher in this rollout. An agent handles Gmail when it is given a Gmail task or an approved scheduler starts one later.

## Permission And Safety Boundary

Maximum normal Google access is capability, not blanket business approval. An agent still needs human approval before consequential external messages; destructive or broad data changes; sharing or permission changes; outside-attendee calendar changes; money, contracts, legal issues, security, sensitive information, angry clients, refunds, unapproved prices; or any unclear action.

OAuth for `jack@zbiz.work` can expose Gmail, My Drive, calendars, contacts, tasks, and Shared Drive content visible to that account. Gmail labels organize work; they do not prevent an OAuth-authorized agent from seeing the wider mailbox. Isolation depends on separate credential stores, runtime controls, profiles, skill rules, and testing.

Google records the shared account as the Google actor. Per-agent attribution must come from the isolated GOG stores and the agent runtime records.

## Failure And Rollback

Stop immediately for a wrong account, wrong alias, wrong label, unexpected data access, failed send block, unwanted message, exposed secret, failed restart, or unplanned change.

- Revoke the affected GOG authorization.
- Disable sending or remove the skill for that agent.
- Preserve other agents' stores until isolation is verified.
- Record the failure without secret values.
- Diagnose the cause, propose the fix, get approval when required, and retest one agent before continuing.

## Completion Standard

The rollout is complete only when:

- Every approved alias exists on `jack@zbiz.work`.
- Every alias routes to exactly one tested `Agent/{AgentName}` Gmail label.
- The shared status labels exist.
- Every approved agent has an isolated GOG store authorized as `jack@zbiz.work`.
- Every agent has an outside profile with the correct alias, label, and sending mode.
- The validated `z-gmail-gog` Skill loads in every approved agent runtime.
- Gmail read, label, draft, correct-alias sending, send blocking, restart, and rollback tests pass as applicable.
- Every agent has its own completion record.
- Any untested item remains marked pending.

## Sources

- Main Notion SOP: https://app.notion.com/p/3cfa3e33d5818176ab4ee0922cc85c50
- Gmail skill repository: https://github.com/ZedBiz44/z-gmail-gog-Skill
- Official GOG documentation: https://github.com/openclaw/gogcli/blob/main/README.md
- Google Workspace alias documentation: https://support.google.com/a/answer/33327
- Google installed-app OAuth documentation: https://developers.google.com/identity/protocols/oauth2/native-app
- Fleet tracking issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/250
