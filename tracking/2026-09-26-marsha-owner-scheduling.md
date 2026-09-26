# Marsha scheduling and helper repair

Date: 2026-09-26. Implemented by Cody, authorized by Jack: "yes fix Marsha".
Technical record: [issue 406](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/406).

## Scope and corrections

Marsha on VPS1 only, OpenClaw 2026.9.4 / base image
`zedbiz/openclaw-base:2026.9.4-9ae62eca-imapfix`.

- The configured MCP scheduling rule excluded every sender ID. Accept Jack's
  existing authenticated owner Discord DM while retaining provenance checks.
- Codex dynamic tool callbacks lost the admitted run context. Wrap exposed
  tools with the existing gateway caller identity wrapper, using the actual
  admitted run and its cancellation signal.
- System-agent nested inference used the main queue. With Marsha holding that
  queue while awaiting her helper, both waited indefinitely. Route helper
  inference to the existing system-agent queue used by its outer request.

No timeout or concurrency setting is added or changed. No other agent is patched.

## Reproducible package

`scripts/marsha-owner-scheduling-20260926.mjs` checks expected source matches,
tests the actual scheduling predicate, and tests callback identity construction.
It writes nothing without `--apply`, and backs up originals before applying.
It deliberately fails on different source versions or a repeated application.

`docker/Dockerfile.marsha-owner-scheduling` creates the derived image without
copying a running container or its injected environment. Minimal build context
contains only the installer and Dockerfile.

Image: `zedbiz/marsha:2026.9.4-owner-scheduling-20260926`.
Image index: `sha256:acd871d0f98c441713c2336efb8b8098545504ac7aa2a0ccfd4cf378a6797451`.
Host build directory: `/opt/openclaw/builds/marsha-owner-scheduling-20260926`.

## Verification and attempts

- Actual patched predicate accepts the existing local-owner route and Jack's
  authenticated Discord DM; rejects other senders, wrong sessions, nonowners,
  delegated or scheduled provenance and supervision connections.
- Binding test retains actual admitted context, session and cancellation signal.
- All three patched modules pass Node syntax checks; derived image builds.
- Actual command queue test completes nested helper work while the parent holds
  main concurrency at one.
- Live helper request passed its previous missing-authority rejection, exposing
  the queue defect. Cody restarted Marsha to release that repair test after
  `chat.abort` returned unauthorized. Restart recovery correctly ran as an
  internal-system turn without owner tools; it is not owner-scheduling proof.
- End-to-end scheduling, helper response and delivery verification pending.

## Rollback and persistence

Runtime originals: `/home/node/.openclaw/backups/marsha-owner-scheduling-20260926`.
Image originals: `/opt/zedbiz-patches/originals`.
Deploy only by changing Marsha's compose image and using her protected
`op-start-marsha.sh up` launcher after her work finishes. Do not use plain compose
with unresolved credentials. Preserve the Asana sidecar and state volumes.
Rollback selects the original base image through the same protected launcher.
Do not roll back persisted user schedules or journal entries with the runtime.
