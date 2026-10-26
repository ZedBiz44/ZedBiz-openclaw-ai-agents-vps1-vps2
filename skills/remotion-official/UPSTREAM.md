# Official Remotion Agent Skills

- Source: https://github.com/remotion-dev/remotion/tree/main/packages/skills
- Upstream commit: `e385a83dbde54179c0457ad90b7d7c3a4b6ab44a`
- Package version: `4.0.532`
- Imported: 2026-10-03 Mountain Time
- Imported by: Cody

The twelve upstream skill folders are preserved with two compatibility changes:

- Removed the optional upstream `version` frontmatter field because the shared
  OpenClaw skill contract accepts only `name` and `description`.
- Links to sibling skill folders use `../` so they resolve from OpenClaw's flat
  workspace skill layout.
- Removed eleven Git symlink placeholders from the router folder. Windows checked
  them out as plain text files; the corrected `../` links replace them cleanly.
- Added the version and source record inside the router folder so Vivian can verify
  package provenance without relying on the removed frontmatter field.

The package contains instructions and examples. It does not install a separate video
editor or paid service. Vivian's `z-video-production`, `z-audio-production`, AGENTS.md,
approval, secret, and no-spend rules remain authoritative.

Review the current Remotion license before commercial production use:
https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

October maintenance adds the ZedBiz delivery and authorization adapter to the router. All twelve runtime skill packages validated; a local H.264/AAC render and decode passed. Existing project dependency locks remain unchanged.
