# Victor host recovery and authorized VPS1 rollout

Date: 2026-10-18 MDT. Operator: Cody. Jack authorized Victor's Amanda-equivalent
repair, evergreen Notion SOP updates, then sequential upgrades and fixes for all
VPS1 agents. Workstreams #467 and #459; source draft PR #470, stacked on #469.

## Victor verified result

The original failed host unit now reports enabled, active/exited, Result=success
after actual service activation and two controlled lifecycle checks. The override
uses the Amanda-tested checksum/image-identity recovery driver and bounded wrapper
retries. Original unit, protected wrapper, Compose and OpenClaw configuration bytes
match the saved originals. Shutdown policy and restart dashboard were not changed.

- Recovery root: `/opt/openclaw/recovery/victor-20261018`.
- Current driver SHA256: `4f03f0f8c82e1f23d654dbfadb44a6bc87d7f430b2ba7f46f087a7e429f6c44c`.
  After lifecycle acceptance, the host-wide image restore lock was added without
  restarting the gateway; the previous driver is retained. Amanda received the
  same lock, SHA256 `5790f5cf80e2c63c5e8a3ee5cc4b251fd79790c6251abe0fc7ad71e601bd097c`.
  The lock covers image recheck/import and is released before wrapper startup.
  Fleet tests passed 11 cases, including two concurrent processes importing once;
  Amanda and Victor each passed their eight recovery tests again.
- Image archive SHA256: `2645f1aee7596b82aaed5ec106e6e19f757a8b25822d72676894cc7afac3f9db`.
- Cold import into independent production-format Docker/containerd storage passed
  all image identities and executable version, in 184.3 seconds.
- Offline state archive SHA256: `b7e7d6fcec730ff0b21ea88ec92101e56e82fb563d42676651d914c8c719f12b`.
  Agent folders and external LanceDB included; ignition token/resolved environment
  excluded. Core/main SQLite quick_check and archive listing passed.
- First cycle had one generic CLI bootstrap/admission exit and automatic Docker
  recovery. No OOM. Actual cause is not exposed by the generic CLI error.
- Repeat cycle used HTTP-only readiness before CLI probes and passed after 211.9
  seconds with zero restarts/OOM. This suggests early CLI contention but does not
  prove causality. Keep the first failure as an observation, not a clean-first-boot claim.
- Accepted container: `4507b20aed03311527c6e19f4c40e20062dcb25aa8e1aa5a57d8cceeff0da661`.
- Pre-change run `fa15aaec-561a-415d-8b1c-eb33495ec549`, first post-cycle run
  `6c33ee49-3ef6-4653-bcf1-a86d6c8031e9`, and repeat acceptance run
  `b2aeec85-b345-4bc6-a63c-333cd0e5b0e0` passed GPT-6.1 Sol without rerouting,
  memory recall, Victor's Asana identity and Notion page access.
- All 26 schedule definitions unchanged; Discord/Telegram connected; public
  health HTTP 200 and Docker healthy. Amanda remained unchanged.
- Post-repeat sample: Victor gateway 1.805 GiB plus Asana 61.22 MiB. This is a
  sample after restart/testing, not a sustained leak or workload benchmark.

Protected receipts: `/home/jackadmin/victor-host-recovery-20261018`.
Rollback removes only the added recovery override and reloads systemd; preserve
recovery archives and current agent state. Any historical 9.8 recovery requires
the matching pre-migration state, never an old image over incompatible new state.

## SOP updates

The maintained procedures are in Notion only. Main creation SOP, Update Procedure,
Docker Base Image Creation and 1Password guide were updated and fetched again.
They now cover next-start image identity, protected archive retention, manifest
refresh, isolated restore proof, service versus application health, HTTP-first
readiness, actual model/tool/memory acceptance and memory measurement limits.
The procedure database and historical child pages were retained. The conflicting
June base-build recipe is prominently marked superseded and routes to current SOPs.

Main: https://www.notion.so/f24a3e33d5818256accd0185fe925af2
Journal: https://www.notion.so/3fda3e33d5818139afb0f6670de372c1

## Fleet rollout completed

Starting inventory: Amanda/Victor already 10.4; Wilma, Vivian, Grogar, Inga, Maggie,
Gohzed, Edith, Terry and Marsha on 9.8. Memory cohorts are LanceDB, Hindsight and
Mem0. Marsha's owner-scheduling derivative and Marsha/Grogar Workshop startup
repair require preservation. Existing standard, advanced and Edith-pagination
Asana variants are retained.

Shared 10.4 image: `zedbiz/openclaw-base:2026.10.4-fleet-20261018`,
ID `cea69c822863f615bf9f106d18212680dd1aa634278ecc30c97466207ca83d83`.
It inherits the verified pilot base and retains the tested dynamic-memory fix.
The old IMAP patch is not transplanted; upstream 10.4 already contains the fix.
Marsha owner/scheduling behavior tests passed on the ported 10.4 modules.
Workshop routing is baked into two separate cohort images, preserving the
existing approved model and replacing the stale startup mutation with verification.
Grogar image ID is `6a2a9dbaf7b27f93da0b2b6264cdfd53d9307d113910dc1c4aadf84e7c9d1ed1`;
Marsha final image ID is `a3371b6255f42a349914938a78bb418e9d89752d1529e00e7070b4b63a1e60a2`.

Shared recovery archive: `/opt/openclaw/recovery/fleet-20261018/images.tar`,
SHA256 `962aa85b90f27240ef9e1701aa7ecb881b2f96c3ecbc9fc2b8d809c9f4d2c619`.
Seven images cold-restored and exact IDs verified in 189.0 seconds. Both new
gateway executables passed version checks. The Workshop archive SHA256 is
`d1b84d3ddab123f39d3259ef4f289f5f31652a8e810229b054b68eb41d0fe257`;
seven exact images and executable versions passed cold restore in 178.4 seconds.
All temporary proof daemons and extracted proof image stores were removed;
protected recovery archives and receipts remain.

Hindsight PostgreSQL custom dump and Mem0/Qdrant snapshot are protected under
`/opt/openclaw/backups/fleet-20261018/shared-memory`. Dump catalogue and snapshot
archive listing passed; this is backup validation, not a shared-service restore test.

Wilma is the first remaining agent. Offline backup and fresh extraction/integrity
passed; archive SHA256 `e21a5401eedd5c2775911f14e7533be9f55aaec211454a21d25f68298eda2104`.
Eight schedules recorded. Both isolated and live Doctor migrations passed, with
schedule rows, model policy, memory backend and MCP preserved. All enabled official
plugins passed the 10.4 version gate. Wilma, Vivian, Inga, Maggie, Gohzed and
Grogar, Terry, Edith and Marsha are accepted. New capability cohorts receive isolated migration rehearsals; matching
agents still receive individual offline backup extraction, integrity/preservation
checks, plugin gates, managed activation and actual runtime acceptance. Every named agent passed; the final simultaneous fleet check also passed.

| Agent | Schedules preserved | Actual acceptance run | Result |
|---|---:|---|---|
| Wilma | 8 | `8c5c167c-5110-4468-aa43-9dda2cda7492` | GPT-6.1 Sol, no reroute; memory, own Asana, Notion, all five command tools; Discord/Telegram connected |
| Vivian | 8 | `59ca76d3-db01-4bdc-aab6-2f31dda056cd` | GPT-6.1 Sol, no reroute; memory, own Asana, Notion, all five command tools; Discord connected |
| Inga | 9 | `77dfddd7-bfa7-48e9-a4a9-f6a5a47da97b` | GPT-6.1 Sol, no reroute; actual Hindsight recall, own Asana, Notion, all five command tools; Discord/Telegram connected |
| Maggie | 8 | `c38fd1c1-b71c-43ed-b6ff-920f1d4253a3` | GPT-6.1 Sol, no reroute; actual Hindsight recall, own Asana, Notion, all five command tools; Discord connected |
| Gohzed | 8 | `e127e3a1-be8d-45fa-8dbe-e3c9f92028ad` | GPT-6.1 Sol, no reroute; actual Hindsight recall, own Asana, Notion, all five command tools; Discord connected |
| Grogar | 8 | `51012656-07b6-4032-acc6-6ad2c8d5706d` | Dedicated Workshop image and startup safeguard passed; GPT-6.1 Sol, no reroute; actual Hindsight, own Asana, Notion and all five command tools; Discord connected |
| Terry | 8 | `849af4d8-560b-41bf-b477-9db7ff086502` | GPT-6.1 Sol, no reroute; actual mem0_search, own Asana, Notion and all five command tools; Discord/Slack connected |

Vivian's rollback archive SHA256 is
`83def7ae89902ae805f5a676214ffa0cf24d3ef1011b1ea3170b95dd8ba1019a`.
The archive is about 22 GiB. Accepted disposable restored copies were removed
for Wilma and Vivian; archives and receipts remain. Vivian correctly identified
her recalled role fact as historical; no memory content was rewritten by this test.
Inga, Maggie, Gohzed and Grogar's disposable copies were likewise removed after acceptance.
Original-archive comparisons for Wilma/Vivian/Inga/Maggie/Gohzed confirmed exact
preservation of tool permissions, channels, gateway authentication and selected
memory-plugin configuration. The same checks were added to the migration gate;
Grogar's live gate passed them.

The original Inga generic-memory run used local Markdown, not Hindsight. It was
preserved separately and acceptance withheld until the backend-specific repeat
passed. The acceptance script now requires agent_knowledge_recall for Hindsight,
mem0_search for Mem0 and memory_recall for LanceDB. Operator CLI sessions have no
stable message provider, so Hindsight automatic recall/retain skips them; explicit
static-bank recall was proved through the agent's own tool. The retained Hindsight
source SHA256 `3402f3b923dbaa4ab6488ee1a93cdac63985b13d50b05c9211216c108ee487a1`
matches a pre-migration archive copy. Its provenance-invalid warning is retained;
no trust override or reinstall was used to hide the warning.

Terry/Edith preflight found the existing Mem0 host-peer helper explicitly gated
to 9.8 and an old hashed module name. The prepared replacement accepts only the
reviewed 9.8/10.4 host modules, retains Mem0 1.2.1 and Qdrant 1.18.0 and leaves the
existing explicit-retention repair intact. A disposable real-module test passed
link creation, idempotence and rejection of unexpected plugin/root values. Its
first nonroot fixture could not read the protected source mount; root fixture
passed, then the fixture passed all four cases under runtime UID 1000 after
copying the test source into the disposable container. The compatibility gate
mounts the separate agent npm storage, matching actual Compose layout.
Terry passed that gate on both restored and live state, followed by actual
mem0_search through his running gateway. Edith passed the same compatibility and consent checks, followed by actual mem0_search.

Terry's Doctor revealed stale capability consent: the October 3 approved surface
listed eight original memory tools, while the already-installed manifest also
declared mem0_search/mem0_get. Original and migrated manifest SHA256 are identical:
`b41def82737a590fe97633e2dbf1c95c1a4e2ad3019257bd16bd0e2b42122309`.
The retained implementation SHA256 is
`0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2`.
Both hashes match Terry and Edith's original files. The supported consent renewal
was gated on these exact bytes and the existing enabled policy, then tested on
Terry's restored tree before live application. Both accepted exactly the existing
ten tools, with unchanged plugin policy and no added channel/provider/hook/MCP/CLI
or dangerous-config capabilities. Consent receipts and command output are retained
under each agent's protected backup directory. No unresolved-consent gateway was
activated. The early rehearsal compatibility check preceded staging of this new
consent check; the live step explicitly repeated restored-state consent proof first.

Terry retained his 22,000-character bootstrap allowance (20,512 characters used),
Mem0 1.2.1, Qdrant 1.18.0 and the existing explicit-retention implementation.
His rollback SHA256 is `874718acbbe891ba5cbe3a0d6abe4c1bb5f2c40df8fadc47f52e81f963614215`.

Read-only cgroup/PSS snapshots distinguish anonymous memory, file cache and
shared-code-adjusted process memory. At 08:04 UTC gateway samples were Amanda
1914 MiB, Victor 1878 MiB and Wilma 1897 MiB. A later sample was 1913, 1775 and
1951 MiB respectively. Victor's earlier excess is absent in these observations;
this does not prove a sustained workload/leak result. Receipts are memory-midrollout.json
and memory-second.json in the protected fleet staging directory.

Edith accepted run `bb141619-dc5a-4d5b-a36a-21ef63d5f30b`: GPT-6.1 Sol with no
reroute, actual mem0_search, own Asana identity (1215564984542462), Notion dashboard
read and all five command binaries. Nine schedules unchanged; Discord connected.
Her custom pagination Asana image and existing 20,000-character bootstrap budget
were preserved. Rollback SHA256:
`db93d8d3650383b4eb8075cdf1cf30f6de00cdd5497af78b6d83e175265f5f28`.

At 03:55 MDT, before Marsha's final activation, the other ten gateways remained
healthy with zero restart/OOM. Docker-comparable memory was Victor 1706 MiB and
Amanda 1977 MiB; proportional process memory was 1638 and 1855 MiB respectively.
The ten running gateways ranged from 1566 to 2013 MiB. This is a later operational
sample, not an equal-workload benchmark or proof that all retained memory is needed.
Receipt: `memory-before-final.json` in the protected fleet staging directory.

## Attempts and retained issues

- Initial fleet image build failed because default docker0 was absent. The offline
  build succeeded with `--network=none`; no production networking was changed.
- Legacy webhooks migration warning is present in Wilma rehearsal, as in both
  accepted pilots. Wilma has no corresponding configured entry/top-level webhooks
  and zero native_hook_relay_bridges rows. Saved migration state is retained;
  the warning is not claimed repaired.
- Memory collector initially failed on a namespace-relative cgroup path; BusyBox
  also lacks nsenter -C. Running the read-only helper with Docker --cgroupns=host
  resolved collection. No production cgroup settings were changed.
- An early inventory command accidentally printed an existing internal memory
  service key into the private tool transcript. Reader changed to whitelist names
  and versions. No key copied into technical records; Jack was informed. Rotation
  remains a separate credential follow-up.
- Local archives survive image pruning, not loss of the VPS disk. No server reboot
  or off-host disaster-recovery test is claimed.

## Marsha acceptance and fleet completion

Marsha's isolated and live migrations passed with all 14 schedule definitions,
model policy, permissions, Hindsight memory settings and MCP settings unchanged.
Her existing 21,285-character bootstrap budget and 600000 ms idle cleanup remained.
Rollback SHA256: `83f12216f238c483edd1ee57ec005cb1107d250ddda3e3bb10903363e01b71bf`.
Accepted container: `339e5e4c726cf85704895f233ae9500f1dded24f393bdcc66de2d24cd0f02bda`.
Run `34fc5f57-5b4e-4f16-9ea8-afdcc29bfe40` used her configured GPT-6 Astra without
reroute (the other ten accepted agents used GPT-6.1 Sol). Actual Hindsight recall,
Marsha Asana identity 1214051396458813, Notion dashboard fetch and all five command
binaries passed. Discord and Telegram are connected. Her three installed scheduling
module hashes match the image build manifest; the actual patched predicate and
caller-binding behavior were tested during image construction. Marsha and Grogar
both logged successful Workshop image verification. This does not claim that a
new live scheduled task or external message was created as a test.

At 04:05 MDT on October 18, final-status.json passed all eleven agents together:
OpenClaw 2026.10.4 (383c124), HTTP 200, healthy gateway and Asana sidecar, exact
selected image identities, verified next-start Compose references and wrapper
checksums, enabled host services with active/exited and Result=success, zero
container restart/OOM, and 600000 ms MCP idle cleanup. All nine new fleet acceptance
receipts still refer to the same running container. Amanda and Victor have their
separate accepted lifecycle receipts above and in the Amanda technical record.
All 126 schedule definitions were preserved across the individual acceptance tests.

Final Docker-comparable gateway memory (MiB, current minus inactive file cache):

| Agent | Gateway MiB | Proportional process MiB |
|---|---:|---:|
| Amanda | 1925 | 1818 |
| Victor | 1704 | 1635 |
| Wilma | 1881 | 1784 |
| Vivian | 1835 | 1765 |
| Inga | 1865 | 1810 |
| Maggie | 1670 | 1619 |
| Gohzed | 1694 | 1628 |
| Grogar | 1750 | 1683 |
| Edith | 1974 | 1846 |
| Terry | 1921 | 1782 |
| Marsha | 2125 | 2027 |

Sample timestamp 10:05:55 UTC / 04:05:55 MDT. Marsha was freshly accepted; these
are operational samples, not equal workloads. Existing RAM limits were retained.
Host available memory was 9350 MiB, with 864 MiB of swap used; free disk was 78 GiB.
Victor's earlier excess is absent; sustained memory attribution remains a separate
open finding. All disposable rehearsal/extracted agent trees are removed after
acceptance. Protected offline state archives, recovery images and receipts remain.

Evidence under `/home/jackadmin/fleet-10.4-20261018/`: `final-status.json`,
`memory-final.json`, `special-final-proof.json` and per-agent release logs.
Per-agent protected backups and actual tool receipts are under
`/opt/openclaw/backups/fleet-20261018/{agent}/`. Latest source syntax validation
passed all 22 staged Python files; five recently changed acceptance/compatibility
files were compared against published GitHub contents and matched. Source remains
in draft PR 470, stacked on draft PR 469; runtime changes are deployed, PRs unmerged.
