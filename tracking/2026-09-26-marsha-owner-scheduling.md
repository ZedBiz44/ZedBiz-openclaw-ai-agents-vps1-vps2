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
- Fresh live run `27af209c-de9c-47fd-8eec-678e027f7f34` completed successfully.
  Marsha herself created monitor `4e93b197-b3a3-4c2b-b579-1598110cf7cb`, read
  back its ten-minute schedule, and triggered its first run.
- Scheduler receipt: status ok, 82,922 ms, delivery status delivered to Jack's
  Discord DM (delivery fallback used). Its own Asana identity, three control
  tasks and 21 participant task/comments were accessible.
- Helper returned after about 49 seconds. Its read-only status call passed.
  It has no scheduler-inspection tool; container `systemctl --user` errors do
  not establish a broken Docker gateway.
- The scheduled run reported missing Codex Apps Notion tools. Normal chat
  Notion access works. `codexPlugins` is absent from Marsha's plugin config;
  scheduled app authority is therefore not captured, and the finite scheduled
  tool list disables native app tools. This is a remaining connector gap,
  not a successful response-proof check.
- Normal inbound Discord has not been tested; the live repair request used
  the authorized operator route. The owner Discord predicate was tested.

## Rollback and persistence

Runtime originals: `/home/node/.openclaw/backups/marsha-owner-scheduling-20260926`.
Image originals: `/opt/zedbiz-patches/originals`.
Deployed by changing only Marsha's compose image and using her protected
`op-start-marsha.sh up` launcher after her work finished. Gateway ready at
11:59:53 MDT; all three live module hashes match the image manifest after
recreation. Compose backup:
`/opt/openclaw/agents/marsha/docker-compose.before-owner-scheduling-20260926.yml`.
Do not use plain compose
with unresolved credentials. Preserve the Asana sidecar and state volumes.
Rollback selects the original base image through the same protected launcher.
Do not roll back persisted user schedules or journal entries with the runtime.

## Remaining decision

Enable the supported connected-app policy for Marsha, reauthorize her existing
monitor from her own fresh owner turn, and test actual scheduled Notion reads.
The available account-app switch affects her connected apps generally; Cody
asked Jack before making that additional configuration change. No account-app
policy was changed in this repair. Monitor remains active with explicit reporting
of the Notion limitation and suppression of unchanged alerts.

Local Git push lacked interactive credentials. The same narrow local commit
was transferred as a Git bundle and pushed using the existing protected server
Git credential; no secrets entered the repository. PR 410 is draft while the
connector gap remains open. Unrelated Vivian branch and Rocky files preserved.
