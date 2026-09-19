# Edith tool locations

The working Google Drive registries are private, per-project files at `/home/node/.openclaw/private/folder-cleanup/<project-slug>/registry.json`. Existing slugs include `laughs-and-fun`, `incanmore`, `albertawide`, and `marketing-tool-comparisons`. Account label: `approved-shared`; client code: the matching slug. Read the actual registry locally; never print or publish its contents. Do not conclude Drive configuration is missing because no registry exists immediately under `private/`.

Read `workspace/skills/z-drive-gog/SKILL.md` and its runtime configuration reference. Run its `drive_preflight.py` using the exact registry, account label and client code. New already-authorized project mappings must be established from the live assigned root ID and approved account, preserving existing configuration; never substitute the entire Shared Drive for a project boundary.

Folder cleanup work uses `/home/node/.openclaw/private/folder-cleanup/` saved plans and checkpoints. Scoped executor code is in `/home/node/.openclaw/workspace/scripts/`. `albertawide/work.py` supplies the shared guarded GOG transport; set its project root/base from the verified task, not the default AlbertaWide values. Copy timeouts use the installed reconciler; never blindly replay a write.

For the current project, forced restart cycles and time-limited production sessions are disabled. Do not invoke the historical dispatcher to arm a backup or successor. An assignment identifies work; it does not authorize reinstating the old timing policy. Use the current explicit work brief and one active writer.

