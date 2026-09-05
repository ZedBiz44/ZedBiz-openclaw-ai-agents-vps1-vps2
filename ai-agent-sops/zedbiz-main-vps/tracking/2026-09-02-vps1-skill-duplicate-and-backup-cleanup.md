# VPS1 Skill Duplicate And Backup Cleanup

Date: 2026-09-02 MDT | Agent: Cody | Status: Superseded on 2026-09-05

> Correction: This record's managed-root recommendation was superseded on 2026-09-05 after checking the official OpenClaw install default and the live VPS1, VPS2, and Rocky layouts. The correct ZedBiz standard is one custom copy in each agent's active `workspace/skills` directory. See `ai-agent-sops/shared-scripts/2026-09-05-openclaw-workspace-skill-standard.md`.

## Purpose

- Remove duplicate active skill packages and prohibited old-skill backups from every VPS1 OpenClaw agent.
- Make GitHub the only rollback and recovery source for custom skills.
- Prevent the fleet deployment script from recreating the problem.

## What Caused It

- The 2026-08-27 Z-Knowledge deployment procedure deliberately copied the same packages into both the managed and workspace discovery roots.
- The old rationale was to prevent OpenClaw precedence from selecting a stale copy during migration.
- The same rollout family also created timestamped server backup trees containing old skill packages.
- This violated Jack's standing instruction that old skill copies must not remain on servers and left OpenClaw with avoidable duplicate discovery choices.

## Live Cleanup

- Affected VPS1 agents: Amanda, Edith, GohZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- Terry and Edith were cleaned and verified first as the required pilot.
- Removed every `skills-retired-20260804` directory found at agent and workspace level.
- Removed all same-name managed/workspace duplicates while preserving genuine workspace-only skills.
- Promoted the current GitHub-authoritative `z-support-doc-ingestion` package into the managed root for Terry, Vivian, and Wilma before removing their older or duplicate alternate-root copies.
- Normalized Wilma's `z-asana-agent-control` to the same minimal managed package used by the fleet, removing its nested repository copy.
- Removed obsolete `small-bite-wiki-research` plugin copies, Cody rollback skill copies, and Marsha's temporary Z-Skill repair tree.
- Removed 225 old skill-package directories from agent backup trees, totaling 11,896 KiB.
- No replacement server backup was created.

## Source Corrections

- This managed-root correction was later found to be incorrect and has been replaced. `deploy-vps1-zknowledge-skills.sh` now deploys shared skills only to the workspace root and removes any same-name managed copy.
- VPS1, VPS2, Ruby, and Rocky Z-Knowledge deployment scripts no longer create server-side skill backups; recovery points to GitHub.
- `ai-agent-sops/shared-scripts/README.md` now states the no-server-skill-backup and one-canonical-copy rules.

## Verification

- Terry and Edith returned successful fresh no-tool model responses after the pilot cleanup.
- All eleven VPS1 OpenClaw containers returned healthy after controlled sequential restarts.
- This verification was accurate for the temporary 2026-09-02 layout, but that layout is no longer the standard. The 2026-09-05 rollout moved the skills to `openclaw-workspace` and reverified all eleven agents.
- Final active-root audit returned zero duplicate skill names.
- Final retired-folder audit returned zero `skills-retired-*` directories.
- Final backup-tree audit returned zero `SKILL.md` files under agent `backups/` paths.

## Recovery

- Redeploy the required skill version from its authoritative GitHub repository.
- Do not restore or create a server-side backup skill folder.
