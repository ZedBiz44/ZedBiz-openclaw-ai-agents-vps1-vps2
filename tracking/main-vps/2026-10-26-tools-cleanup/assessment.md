# Retired TOOLS.md cleanup

Date: 2026-10-26 | Agent: Cody | Status: Live verified; PR open

## Result

- All fifteen OpenClaw agents on VPS1, VPS2 and VPS4 were on 2026.10.6 and already had migrated local notes in AGENTS.md. None had an active standalone TOOLS.md.
- Corrected 52 instruction lines in 23 active core files. Each AGENTS.md Tools block remains byte-identical to its pre-cleanup content. Identity, role, privacy, approval and task conditions were retained.
- Amanda passed the first fresh-session pilot before expansion. All fifteen agents then passed fresh-session behavioral checks for the current notes location, missing-legacy-file handling, role, diagnosis boundary, source routing, unique safeguard and a final-section rule.
- All changed files match their prepared hashes; owners and modes are preserved. Other inspected core files remain unchanged. No active obsolete references remain in the inspected core instructions. Historical source labels, migration headings, archived startup material and personal history were intentionally retained.
- Relevant workspace skill/script scanning found only the health-policy mention describing migration findings; that is not an instruction to read the retired file and was retained.

## Scope and source

Jack explicitly authorized cleanup across VPS1, VPS2 and VPS4 after reviewing the diagnosis. The exact candidates were derived from live workspaces, not older reference files. The main repository did not have a tracked current agents/amanda/AGENTS.md at the probed route; these dated candidates and diffs preserve the tested live state without overwriting older unrelated snapshots.

Existing workstream: [issue 498](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/498). Fleet source: [PR 503](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/503). Rocky cross-reference: [VPS4 issue 63](https://github.com/ZedBiz44/ZedBiz-openclaw-vps4/issues/63).

The installed doctor-tools-md-migration module confirmed that OpenClaw rewrites an enumerated set of standard phrases. Customized wording survived the earlier migration. No broad Doctor repair was necessary.

## Preservation and verification

- register.json records baseline/candidate hashes, counts, owner, mode and exact paths for each change.
- candidate/ contains the complete prepared files and narrow unified diffs. Replacement changed routing only; no rules or migrated notes were deleted.
- deployed/ records protected timestamped backups and read-back hashes. Restore the exact originals from the listed backup directory to roll back; preserve recorded ownership/mode and confirm baseline hashes.
- final-file-checks.json verifies changed and unchanged inspected files, permissions and absence of the retired active file.
- verification.json holds filtered fresh-session replies, isolated session IDs, configured provider execution receipts and analyzer results. All sessions used their resolved intended workspace, completed without fallback, and demonstrated the revised behavior.
- Several files exceed the skill's 14,000-character recommendation because of already-migrated content. All remain below their existing live per-file limits. No limit, hook, runtime configuration, model, integration, provider or schedule was changed.
- Native AGENTS.md reporting remains native_unverified, with null injectedChars/truncated. Behavioral answers and final-section checks passed; do not reinterpret those metadata fields as an instrumented guarantee that every character was injected. No full-context injection claim is made.
- VPS1 gateways and Asana services were healthy in the closing sample. VPS2 Frank/Harry/Suzy and VPS4 Rocky services were active/running with zero automatic restart counts. This cleanup issued no gateway restart.

## Attempts and limitations

- One backup directory required container-root access. The write stopped before touching that target; the existing Docker administrator route created its protected backup and preserved original file ownership/mode.
- Batch resumption initially included already-completed agents. Baseline checks rejected those repeated writes; retained deployment receipts identified completed targets and pending work resumed. An idempotent receipt/hash check was added to the local deployment helper.
- Inga's first test encountered a stopped container during independent VPS1 maintenance. No restart was issued here. After she returned healthy, a new isolated session passed.
- Initial native-host discovery confirmed VPS2 has no Docker; native systemd paths were used. Rocky uses the openclaw user service.
- Desktop Git publishing lacked usable authentication. The saved local credential attempt also failed without exposing its value. Local commits were transferred as Git bundles and published through Victor's existing authenticated admin Git route; no agent message or credential change was involved.
- Local skill validation first found missing PyYAML, then an incorrect temporary package folder name. PyYAML was installed only in the task's temporary validation directory, and the correctly named runtime package passed both validators. Legacy source repository lacks a README; package validation, rather than a claim of full repository-policy compliance, is reported.
- A local report subprocess initially used the Windows default output encoding; UTF-8 was set and the analyzer/report passed. Patch files contain standard unified-diff blank context lines, which Git's whitespace check flags as trailing spaces in the patch artifact itself; candidate content was not rewritten to remove those markers.

## Skill and operational records

The AGENTS.md Manager now explicitly covers preservation, outdated references, no recreation of the retired file, version checks, one-agent testing and existing-scope rollout. [Skill PR 2](https://github.com/ZedBiz44/z-openclaw-agents-md-manager-Skill/pull/2), commit 8f2aa43b4716c9e47bcf7d21631f5e738f43f6b4. All eight installed Codex runtime files match the commit's text; both package validators passed. The Notion SOP was updated in place, preserving its other content.

GitHub PRs are open, not merged. Live cleanup is verified. Issue 498 remains open for separate memory/finalization problems, which this cleanup does not claim to fix. Registry identity and infrastructure configuration are unchanged. Older conversation history may still remember the retired path; fresh sessions now demonstrate the corrected instructions.
