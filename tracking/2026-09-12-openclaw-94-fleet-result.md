# OpenClaw 2026.9.4 fleet deployment

2026-09-12 MDT | Cody | Complete: all fourteen authorized agents upgraded and verified

## Scope and result

Jack authorized Terry and Harry first, then the remaining VPS1 OpenClaw agents, then Suzy and Frank after VPS1 finished. All eleven VPS1 agents plus Harry, Suzy and Frank now run the qualified 2026.9.4 release and passed their live integration tests. Suzy and Frank also passed explicit Hindsight recall after clean service restarts. Rocky and host reboots remain outside this deployment.

The final VPS1 sweep returned version 2026.9.4, Docker healthy, zero restarts and public HTTPS 200 for every agent. Each completed agent also passed an actual model turn, memory recall, its own Asana PAT identity, explicit Google account checks, installed IMAP behavior and post-upgrade configuration checks. Service health alone was not treated as integration proof.

The final VPS2 sweep returned version 2026.9.4, active/running services, NRestarts0, public HTTPS200, no post-upgrade Doctor findings and the exact patched IMAP checksum for Harry, Suzy and Frank. Machine-readable evidence is retained at /root/openclaw-fleet94-20260912/final-native-health.json. VPS2 has approximately 118 GB free.

The subsequent [Notion search diagnosis and correction](2026-09-12-notion-search-correction.md) supersedes the earlier claimed search limitation. All fourteen agents passed actual AI search and opened a returned page in fresh conversations. The repair added only a bounded search-routing note to their existing instructions; the upgrade itself had preserved those instructions as recorded below.

- [Authorization, investigation and running evidence](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/311)
- [Release implementation and procedures](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/312)
- [Detailed Terry/Harry pilot evidence](2026-09-12-terry-harry-2026-9-4.md)

## Agent acceptance results

All listed completed tests used the agent's own runtime and credentials, without message delivery. Asana workspace: 11298561585567. Google account: jack@zbiz.work.

| Agent | Memory proof | Own Asana identity | Additional evidence |
|---|---|---|---|
| Terry | Mem0 search plus synthetic add/recall/delete | terry@agents.zbiz.ca | Real Gemini short-video analysis; Chromium page load; local FFmpeg; clean restart |
| Edith | Mem0, 3 hits | edith@agents.zbiz.ca | Drive and governed Notion search/read |
| Amanda | LanceDB, 5 hits using runtime owner main | amanda@zedworks.com | Preserved agent-only session visibility |
| Marsha | Hindsight, 4 hits | marsha@agents.zbiz.ca | Drive, Notion and video tool discovery |
| Maggie | Hindsight, 2 hits | maggie@agents.zbiz.ca | Drive, Notion and video tool discovery |
| Inga | Hindsight, 1 hit | inga@agents.zbiz.ca | Drive, Notion and video tool discovery |
| GohZed | Hindsight, 4 hits | gohzed@agents.zbiz.ca | Direct Notion page read; subsequent AI-search verification passed |
| Grogar | Hindsight, 4 hits | grogar@agents.zbiz.ca | Direct Notion page read; subsequent AI-search verification passed |
| Wilma | LanceDB, 5 hits | wilma@agents.zbiz.ca | Existing AllZed AI Engine MCP returned one post read-only |
| Victor | LanceDB, 5 hits | victor@agents.zbiz.ca | OpenSSH 9.2p1 and Docker client/server 29.7.2 |
| Vivian | LanceDB, 5 hits | vivian@agents.zbiz.ca | Percify 11-tool discovery; local FFmpeg clip verified at 1.000000 seconds |
| Harry | Mem0 search plus synthetic add/recall/delete | Harry Zagent | Real Gemini analysis; Drive 4 files; clean restart |
| Suzy | Hindsight, 4 hits before and after clean restart | Suzy Zagent | Drive 3 files; direct Notion read; Gemini discovery; clean restart, public HTTPS200 |
| Frank | Hindsight, 1 hit initially; 4 after clean restart | Frank Zagent | Drive 3 files; direct Notion read; Gemini discovery; clean restart, public HTTPS200 |

## Preserved behavior

- Compared original and upgraded instructions, model routes, memory slot/configuration and session visibility. Amanda retains agent visibility; other VPS1 agents retain tree. Native agents retain the previous effective tree boundary explicitly.
- Kept new Swarm and agent-to-agent defaults disabled and previous maximum spawn depth 1 explicit.
- Preserved each protected op-run startup route, agent account, custom workspace tools and systemd overrides. No credentials were printed or rotated.
- Mem0 stays 1.0.16 with Qdrant JS 1.18.0 compatibility guards; Hindsight stays 0.11.1 with existing banks and backend. LanceDB retained its shared store and owner identities.
- Updated separately installed OpenClaw plugins to exact 2026.9.4 packages and renewed existing third-party plugin capability consent where required. No blanket third-party plugin or skill update.
- Retained the persistent metadata-first IMAP correction. Every completed agent's installed mailbox probe passed two idle sweeps with no old-message source downloads and one simulated new-UID fetch, without sending email or modifying the watcher cursor.

## Qualified artifacts

- Core: 2026.9.4, upstream commit 3a9d69db306cd7f081e06254cb89c4bcc14a7107.
- Official Linux amd64 manifest: sha256:6bc0bf3117e1c5074db8a064084a5f9d41ece1aa2a16369a82f53207b846a5c3.
- npm integrity: sha512-lTQpEEe1Xm3u2PCHaPEr+vP8paGk1vLdHuzdItsNToaLI6hAqRVvgJYg+GxukJhETJp4tPy/S1Gftl4KuB8n7A==.
- Patched IMAP bundle SHA256: 280c7f32fbd8911abb96338a891ac869394357e500c4a24366e0d7f325ed3bea. Four deterministic regression tests passed.
- VPS1 base image: zedbiz/openclaw-base:2026.9.4-9ae62eca-imapfix, ID sha256:e63fb250d64e1e9c257b750daded1e78dfc6332b435c6cd2897fbebe350b4ff9.
- Terry/Vivian image: zedbiz/openclaw-base:2026.9.4-9ae62eca-video-imapfix, ID sha256:9fd61ebc98bccd35f0953d5e7f372997a518e55b8f19c86bab7b317ede891b44.
- Victor image: zedbiz/openclaw-victor:2026.9.4-9ae62eca-ssh-imapfix, ID sha256:7b840386824721582c15dbe987cf3563154a4d61ebe8f2ef1a6952a618f55c3f.
- Native VPS2 candidates reuse Harry's qualified same-host dependencies and checksum-verified patched bundle, while retaining each agent's own package identity and startup files. No Harry state or credentials copied.
- Approved Gemini server annotation fix SHA256: 1f3ba488320b92223e27cc35b99675e0408984c0fd730499128a3a141cf07cc5. Existing auto approval retained. One real 19-second clip passed through Terry (3,261 tokens) and Harry (2,736 tokens), gemini-3.8-flash, store:false.

## Recovery evidence

Each cutover used an offline full-state backup, extracted restore proof and copied-state migration before promotion. Old installations, agent state and Docker images remain available. Private backup contents include secrets and must not be published.

| Agent | Original archive SHA256 |
|---|---|
| Terry | 029a2d81a412893b848cf5ea33e33ad65ba8722672a70b45b4016f14fe90537d |
| Edith | 91ab8ccf38f5095b0e91c24edb0bff38bf476877c60f4ac875ac36824426b195 |
| Amanda | c438694b4d4550567c0026c37a4c395f31a064c2e70ab5b77c2804a91c968ed7 |
| Marsha | 9b4e6f37fb5f606ffa271ab555951909ae0993fcb23be5448bad616067e37dbc |
| Maggie | 894e5af233e2e1ec82810c608a609a1cb87f70d41c0d956a7fd26a608e0e018e |
| Inga | daa37e844f146fbacf85b55d26d482da1d45917022eafe6d0e3d797b6d078580 |
| GohZed | 58fa67fd19595ca7a9457c541fb4127c8fedae2956144f117d05571ee3ae507c |
| Grogar | 087fb2179a5d8a41393e3f4a9b3df305e1a9510090ffe9046e2576ed866bf8fa |
| Wilma | 36fb2a6f519f6354f04a04cb3a2156754e858e8c64f8b344b0b2f9b0e0ce6aa7 |
| Victor | 02c26c7146de69e745668968569c87dc7480d5ba5192dfcdf9f36ee575e725d9 |
| Vivian | a080c9876375b83566375d797eae73091143cdb7e3666c0e7428920ca4992ecc |
| Harry | ce0ce9d8bede7ea72d23cfa4d47a1e91fdbf0764dfbeb55f4c0682085b3b3f98 |
| Suzy | 31ffa7e11712762951e902de481bd701a17011b31aa486fe339968e28fdef5d4 |
| Frank | 83dbb15085896c5d0300249aa46fa1e9d888182f077d7232b6d1c619a537f90f |

- Terry backups: VPS1 /home/jackadmin/openclaw-backups/pilot-20260912-terry-harry.
- Remaining VPS1 agents: /home/jackadmin/openclaw-backups/fleet94-20260912/AGENT; previous directories are retained in original/. Logs include final-audit.json, live-test.json, live-imap.json and post-upgrade/plugin results.
- Harry: VPS2 /root/openclaw-pilot-20260912; previous install /opt/openclaw-harry.pre94-20260912.
- Suzy/Frank: /root/openclaw-fleet94-20260912/AGENT; previous install /opt/openclaw-AGENT.pre94-20260912 and state /root/.openclaw-AGENT.pre94-20260912 after successful cutover.
- Shared Mem0 snapshot SHA256: 47e1d0b295281ae6f62b10fef6f899dd7203b8ce74e342945a99f0c6ac2d6f04. Coordinate any shared-store restore; do not roll back other agents' newer writes.
- Shared LanceDB snapshot SHA256: 35b49c3ed468a44fc3860ecabc29c476dd74e71fcf2579da0b59698d212311be. Restored and opened using the actual 9.4 bundled library: Amanda62, Victor61, Wilma28 and Vivian128 records. Snapshot and proof are under the VPS1 fleet backup root.
- Verified archive compression is used to recover disk headroom: each gzip is fully decompressed and checked against the original tar SHA before the duplicate uncompressed tar is removed. Original agent folders remain retained.
- All eleven VPS1 fleet archives (ten agents plus Wilma's retained first attempt) completed compression verification. Vivian's gzip SHA256 is b32e04cf3615c47ac2f9f290d2524a8be02b1d6b40f8b5029639711fad045207; its restored tar hash matches the table. VPS1 has approximately 45 GB free after compression. A stale local SSH connection was closed only after the server process had finished, its verification metadata was read back and duplicate-tar removal was confirmed.

## Procedure corrections and encountered issues

- GitHub-managed IMAP patch, regression tests and live probe are build inputs rather than a temporary container edit.
- Copied-state checks accept existing plugin capabilities and archive only verified-empty Workshop backup manifests, retaining their original data.
- Wilma's first attempt hit a root-owned copied backup directory; the old 8.2 service restarted safely. The established root-helper route was fixed and tested, then a fresh offline backup and retry succeeded. First-attempt evidence remains retained.
- LanceDB tests use the real runtime owner main, not the agent's display name. Amanda's corrected query returned 5 results.
- Victor's live build recipe now pins the qualified base and preserves Docker CLI29.7.2, avoiding the old loose floating-latest recipe.
- Vivian's first wait expired before her 180-second Docker health interval. Direct health was already live; Docker subsequently reported healthy with zero restarts. The helper now derives its wait from the configured interval. Remaining checks completed successfully.
- Native copied-state commands run in private mount/process namespaces with the agent's own protected environment and canonical paths. Their original startup wrappers remain unchanged.
- A GOG command-form error in Harry's test was corrected to the installed drive ls command without account changes.

## Limits and follow-up

- The earlier Notion search limitation was a false diagnosis caused by tool-naming guidance and an overrestrictive verification prompt. The existing Codex Apps search entry point returns AI-search results. After the routing correction, all fourteen agents passed actual search and returned-page fetch tests; saved tool receipts were independently checked. No new connector, account, permission or package was required. See the linked correction record above.
- GohZed had a transient memory recall timeout warning on a subsequent Notion follow-up; his explicit Hindsight acceptance query had already returned 4 hits.
- Suzy's additional post-restart general memory-search call timed out after 15 seconds. Explicitly testing her selected Hindsight tool openclaw__agent_knowledge_recall then succeeded with 4 results. No memory configuration, bank, timeout or index was changed. Deep CLI status showed main embeddings/vector storage ready; the separate mail_reader built-in index lacked metadata, while memory-core is disabled as the selected memory slot is Hindsight. No unrelated reindex was run.
- Wilma's alternative generic WordPress helper reports a missing key. Her selected AllZed AI Engine route passed a real read and was preserved; no token rotation or connector replacement was made.
- Channel initialization was checked, but no fresh outbound Discord/Slack delivery or incoming-email assignment was induced. Percify discovery and local FFmpeg were tested without paid media generation.
- Terry's full Doctor lint had six pre-existing warnings and no error findings; no broad automatic repair, TOOLS.md merge or credential relocation was performed.
- Deployment source is published on the PR branch; repository main has not been merged by this rollout.
