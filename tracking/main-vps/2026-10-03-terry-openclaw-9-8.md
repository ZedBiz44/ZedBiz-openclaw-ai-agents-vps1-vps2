# VPS1 OpenClaw 2026.9.8 and GPT 6.1 Sol rollout

Date: 2026-10-03 | Agent: Cody | Status: Rollout verified; VPS1 kernel reboot pending

## Scope

Jack authorized the overnight OpenClaw release on Terry with GPT 6.1 Sol, plugin, skill and tool updates, server package maintenance, and a restart report. He narrowed the work to VPS1, then approved GPT 6.1 Sol for all VPS1 agents except Marsha. The other agents also need OpenClaw 9.8 for its Sol runtime catalog. Marsha remains on 9.4/Astra. No host reboot is included.

- Agent record: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/436
- Host record: https://github.com/ZedBiz44/ZedBiz-general-tech-issues-updates/issues/94
- Journal: https://www.notion.so/3eea3e33d581814bb8a5faa6ae82ef9e
- Official release: https://github.com/openclaw/openclaw/releases/tag/v2026.9.8

## Before the change

Terry ran OpenClaw 2026.9.4 (3a9d69d), image `zedbiz/openclaw-base:2026.9.4-9ae62eca-video-imapfix`. Primary model was `openai/gpt-6-astra`, thinking `low`. Fallbacks were GPT 5.6 Terra, GPT 5.6 Luna, Gemini 3.1 Flash Lite, and DeepSeek V4 Flash, in that order. Mem0 was the active memory plugin at 1.1.0. Nine external OpenClaw plugins were pinned to 2026.9.4.

## Image and tools

- Rebuilt `docker/Dockerfile.base` from official OpenClaw 2026.9.8. Official image digest: `sha256:d0ded1dd76939b2bf4d67ef2d13247b8b160aa5666331d4a0b0e58811182cbb8`.
- Refreshed version pins using official GitHub releases, npm and PyPI metadata.
- `docker/Dockerfile.terry` preserves the deployed IMAP fix. The upstream 9.8 bundle still fetches old message sources before filtering UIDs. The preserved fix filters UIDs first.
- Behavior tests passed for quiet inbox, empty inbox, new messages with UID gaps, and retry cursor retention.
- Staged and version-tested shared tools: gog 0.43.0, ntn 0.23.17, ripgrep 15.2.0, jq 1.8.2, mcporter 0.14.2, summarize 0.25.0. Existing wrappers and account settings are preserved.
- Retained Himalaya 1.2.0: version 2.2.1 rejects the existing `account list --output json` command. Its major-version migration requires a separate compatibility change.
- Official ClawHub mcporter skill remains current at 1.0.0. The old unqualified slug now resolves to several publishers; checked `@steipete/mcporter`. Custom ZedBiz skill files are preserved.

## Host maintenance

VPS1 installed 48 package upgrades and six new kernel packages, with zero removals. Docker is 29.8.2. `apt list --upgradable` is empty, `dpkg --audit` is empty, and systemd reports no failed services. All ten non-Terry agents passed direct health requests after the Docker restart and kept their existing image tags.

VPS1 requires a reboot for kernel 6.8.0-146. No reboot was performed. Detailed package logs and before/after inventories are under `/var/log/zedbiz-maintenance-20261003/`.

## Backup and migration

- Protected full offline backup: `/opt/openclaw/backups/terry-20261003-pre-9.8/terry-state.tar`, with SHA-256 manifest beside it.
- Shared tool backups: `/opt/openclaw/backups/shared-tools-20261003/`.
- Build and diagnostic evidence: `/opt/openclaw/builds/2026.9.8-terry-20261003/`.
- OpenClaw Doctor upgraded the three existing agent databases from schema v19 to v24. It also creates pre-migration database backups.
- Rollback must restore the full protected pre-upgrade state and original image together; the old runtime must not be started against migrated databases.

## Verified result

- All eleven VPS1 agents pass Docker and direct HTTP health checks after the completed rollout. No failed systemd services or package audit findings remain.
- Terry's default is `openai/gpt-6.1-sol@openai:api-key-backup`, thinking low, with the original four fallbacks. Fresh default run `62815eec-5977-4f57-97c7-0dedd249ae0b` completed `bash` and `mem0_search`, zero tool failures and `fallbackUsed=false`.
- The initial Sol test encountered a subscription OAuth rejection and rotated to the existing paid API profile. Jack then approved that route. Pinning the primary model to that existing profile gives direct Sol execution without fallback. Terry's credentials and global auth order were unchanged. Edith lacked the profile; added her own existing protected API key through the supported auth CLI after backing up her auth databases.
- Amanda's first model-only test on 9.4 rejected Sol locally and fell back; the script restored her original configuration. After upgrading to 9.8, run `ede640a0-9465-4ce5-b0a7-195c1de11842` passed `bash` and `memory_recall` on exact Sol without fallback. Her schedules, fallbacks, thinking, memory slot and skill settings match the protected backup.
- The expanded rollout covers Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Terry, Victor, Vivian and Wilma. Each passed an exact Sol default run with shell and its own external memory tool: `mem0_search`, `memory_recall`, or Hindsight `agent_knowledge_recall`. Marsha retains her 9.4 image and GPT 6 Astra.
- All official external plugins in each upgraded agent converged to 2026.9.8. Edith's existing patched Mem0 1.1.0 and the four Hindsight agents' 0.12.0 plugin remain in place; their external recall passed. Terry's separate Mem0 update is 1.2.1. No memory-provider migration was performed.
- Wilma's first run encountered an invalid saved API key, then OAuth rejection and Luna fallback. Her own existing protected `OPENAI_API_KEY` passed a direct Sol model-access probe. Backed up her auth databases and refreshed the profile through the supported CLI. Restored her original global OAuth order; only the Sol primary is pinned to the API profile. Subsequent Sol proof passed without fallback.
- Nine installed official external plugins are at 2026.9.8; Mem0 is 1.2.1 with the preserved fixes below. Discord, Slack and IMAP connected after startup. The existing Slack shared-app connection warning remains; no Slack routing redesign was attempted.
- All six scheduled jobs retain the same IDs, names, enabled flags and schedules.
- Eight custom skills received 13 reviewed file updates. No missing skill requirements; eligible count 56. The custom skill files were unchanged by OpenClaw itself before these separate authorized updates.
- Registry versions/model relations and the expanded VPS1 deployment record were reconciled: https://www.notion.so/3eea3e33d58181b19bbac80e632e51b1. The shared historical 9.4 deployment record remains for Marsha and agents outside this rollout.
- Sanitized execution traces, fleet health and reviewed skill file checksums are in `2026-10-03-terry-evidence/`. Full runtime evidence stays in the protected server build directory.

## Custom skill updates

Updated `z-ai-skill-developer`, `z-audio-production`, `z-biz-plan`, `z-files-folders`, `z-video-analysis`, `z-video-critique`, `z-notion-knowledge-publish`, and `z-small-bite-task`. Reviewed current GitHub source changes, deployed only selected runtime files, checked the pre-write checksum against the inspected copy, and verified saved checksums. Package-building scripts and test fixtures were excluded. Backup: `workspace/.cody-skill-update-backups-20261003/`.

Retained Terry's newer `z-record-knowledge` wording: upstream would regress substantive memory retention and read-back requirements. Held `z-knowledge-routing`'s new native adapter because it routes prompts to GitHub, conflicting with Jack's Notion-only rule. Retained `z-code-allocation` because its differences are whitespace and a newline-escaping regression, not a useful upgrade. Other inspected sources already match. Custom skills without a verified current source were preserved and are not claimed as freshly released packages.

The first skill-backup location was root-owned and rejected creation before any skill writes. Switched to a new backup directory inside Terry's existing writable workspace; no permission broadening was required.

## Compatibility corrections

- Compose hardcodes the Terry image. Updating `.env` alone did not change it. The old binary refused the migrated configuration; it was immediately stopped, then the literal image was updated to `zedbiz/openclaw-base:2026.9.8-terry-20261003-imapfix` and the protected startup wrapper recreated Terry.
- Doctor merged TOOLS.md into AGENTS.md (20,512 characters). `bootstrapMaxChars` is now 22,000 to preserve that existing content. The offline maintenance command lacked protected credentials and disabled the Whisper skill; its original enabled flag was restored. Later maintenance commands carry the existing protected environment without printing values.
- Mem0 1.2.1 installed successfully but initially failed live loading. It does not declare an OpenClaw peer, while 9.8's retained native loader requires the host link. `repair-mem0-host-peer.mjs` uses the installed OpenClaw link function to point the managed project to `/app`; the runtime host validation remains enabled.
- The plugin upgrade replaced Terry's Qdrant JS pin with 1.19.0, which removes `search()`. Restored the tested 1.18.0 dependency. The existing exact-match explicit-retention, unique `mem0_search`/`mem0_get`, ID receipt, and recall-limit repairs now also accept reviewed Mem0 1.2.1. Startup validates these safeguards. A root-owned script required Docker root for deployment; the repair was then checked as the ordinary node user.
- Metadata-only `plugins list` does not establish runtime health. After correction, the gateway logged Mem0 registration and initialization in open-source mode with the original user, auto-recall and auto-capture settings.
- The migrated `modelPolicy.allow` list initially rejected the new model override. Added only `openai/gpt-6.1-sol` to the existing list. Model runtime binding is Codex; the primary is changed only after exact-model proof.
- Native plugin cold loading takes about 90 seconds and temporarily blocks health/CLI requests. Wait for the completed startup or reload before testing. This is recorded as a maintenance limitation, not hidden by increasing timeouts.
- Before the separate reviewed skill updates, all custom SKILL.md hashes matched the baseline. Eligible skills changed from 57 to 56 because upstream removed `taskflow` and `taskflow-inbox-triage` and added `visualize`; no missing requirements. [Upstream Tasks/TaskFlow retirement](https://docs.openclaw.ai/releases/2026.9.7).
- Amanda's LanceDB plugin needed the same managed host-peer repair. Her older startup repair referenced 9.4 bundle filenames. The separate inference lane and configured timeout are now upstream; retained her existing live-owner recovery guard with exact source and syntax assertions. Her configured timeout remains zero. Grogar has a separate Workshop repair; its existing model choice is preserved while adapting the verified module filename.

Shared host/tool maintenance and the expanded model rollout are scoped to VPS1. Full per-agent offline backups preserve rollback together with the old image. Before Jack narrowed scope, VPS2 received routine OS packages; Harry's drained service needed a restart and subsequently passed health verification. No further VPS2 work followed the scope correction; VPS3/VPS4 were not changed by this chat.
