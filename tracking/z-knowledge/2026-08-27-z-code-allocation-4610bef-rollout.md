# Z-Code Allocation 4610bef Fleet Rollout

Date: 2026-08-27 MDT
Agent: Cody
Status: Complete

## Purpose

Deploy the repaired canonical `z-code-allocation` Skill and prove that a genuine lookup miss is a normal result while real failures remain errors.

## Source

- Repository: `ZedBiz44/z-code-allocation-Skill`
- Pull request: `ZedBiz44/z-code-allocation-Skill#1`
- Commit: `4610bef71094409ea1d4e8b63f040bbab076726a`
- GitHub rollout issue: `ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2#203`

## Package Verification

- Repository validator passed in repository mode.
- Generated-package validator passed.
- Node.js and Python semantic tests passed.
- Default package-build regression passed.
- `SKILL.md` SHA-256: `39f950e498bc2d293bf49bfea395d404715a07d88f13eb895f3d3ae990eb3c47`
- Node helper SHA-256: `c7f12e2041f866ae809360bd979a6dad361047dcff81be404833176a9937d4f0`

## Deployment

- VPS1: Amanda, Edith, GoHzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2: Frank, Harry, and Suzy.
- VPS3: Ruby/Hermes.
- VPS4: Rocky/OpenClaw.

Terry was the first OpenClaw pilot. Frank was the VPS2 platform pilot. Every replaced Skill folder received a timestamped backup before deployment.

Ruby was restarted through `/usr/local/sbin/ruby-maintenance`; returned change ID `b671b88c-1441-439e-b614-36b8148035b1`.

Rocky was registered as the sixteenth allocator client with a unique credential. The registry backup is `api_keys.json.bak-rocky-20260827-1736-MDT`. Rocky's protected configuration is `/home/openclaw/.openclaw/.env.zcode`, mode `600`, loaded by `zcode-allocator.conf` in the OpenClaw user-service drop-in directory. Credential values were never printed or committed, and temporary transfer files were deleted after installation.

## Live Verification

- Terry direct lookup miss: `found: false`, exit `0`.
- Terry fresh-agent check: normal miss, no mutation.
- Frank direct lookup miss: `found: false`, exit `0`.
- Ruby direct lookup miss: `found: false`, exit `0`.
- Rocky direct lookup miss: `found: false`, exit `0`.
- Rocky fresh-agent check: normal miss, required configuration present, no mutation.
- Malformed lookup remained nonzero on every platform pilot.
- All VPS1 containers were healthy with restart count `0` and `OOMKilled=false`.
- VPS2 services, Ruby, and Rocky were active after deployment; no unexpected restarts were recorded.

No test allocated, reserved, confirmed, failed, or published a Z-Code or Notion record.

## Rollback

- Restore the timestamped Skill backup for the affected agent and reload that runtime.
- For Rocky, restore the prior `.env.zcode` or service drop-in from `/home/openclaw/.openclaw/backups/zcode-credential-rollout-20260827-1738-MDT` when present, then reload and restart the OpenClaw user service.
- To revoke Rocky, restore the protected allocator registry backup on VPS1, restart `z-code-allocator`, remove Rocky's protected runtime injection, and verify that Rocky receives an authentication or configuration failure rather than allocating manually.
- Never restore or share another agent's key.
