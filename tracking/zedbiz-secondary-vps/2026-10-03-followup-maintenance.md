# VPS2 follow-up maintenance — 2026-10-03

## Asana dependency repair

The four high audit entries were one braces denial-of-service finding propagated through chokidar, Babel CLI and Asana. Asana 3.3.0 ships prebuilt runtime files but declares its older build CLI as a production dependency.

The tested package now pins jsdom 30.1.1 and esbuild 0.28.2, with a scoped `asana -> @babel/cli 8.0.6` override. Babel CLI 8 uses chokidar 5, removing the braces dependency chain. No Asana downgrade and no audit suppression were used. The deployed service uses Asana's prebuilt dist; rebuilding Asana's own upstream source is outside this service's build process.

Validation: TypeScript typecheck, service build, valid/invalid Asana rich-text XML cases, isolated Suzy MCP identity/tool/task reads, then sequential Suzy/Harry/Frank production identity, 47-tool listing and task reads. Full npm audit, including development packages, reports zero findings. Original service is retained for rollback.

## Harry memory compatibility

Mem0 1.2.1 candidate retains the existing Qdrant 1.18.0 search API and HTTPS port correction. The explicit-retention patch is version-gated to 1.1.0 and 1.2.1; it preserves exact selected facts, metadata, returned memory IDs and unique mem0_search/mem0_get aliases. Existing automatic recall/capture, user namespace, collection and model configuration remain unchanged.

Isolated validation recalled five existing memories, saved and retrieved one exact test fact under a random temporary user, and removed that test record. Initial harness corrections were Linux line endings and resolving the installed OpenClaw SDK. The first managed update required capability consent and rolled back. Manifest review found unchanged declared memory functionality; the reviewed retry renews consent for the new package. Fresh state backup retained.

## Cleanup and host

Historical recovery content is compressed and verified before original folders are removed. Test/staging copies are removed from their old paths after process-use checks, with compact recovery copies retained. Current full recovery backups remain available. Final evidence records completed cleanup and service checks.

Ubuntu package lists refreshed. Eight packages remain vendor-phased; no eligible normal upgrades and no reboot marker. Phasing was not bypassed.

Records: [issue 429](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/429), [PR 438](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/438), [Cody journal](https://www.notion.so/3eea3e33d581814bb8a5faa6ae82ef9e).

The former startup helper selected the newest directory by modification time and initially patched an older generation. The systemd pre-start command now targets the verified 1.2.1 generation explicitly. Any future managed generation update must update that path after testing. Startup logs confirm the 1.2.1 guard runs before the gateway. The first live probe was attempted during cold startup and timed out; it was retried after gateway responsiveness and Discord probing.


## Final verified result

Harry's production run `2cc09e5b-e31c-48a1-8915-36a87d854333` used GPT-6.1 Sol and mem0_search successfully, returned MEMORY_OK, and had no model fallback or tool failures. Mem0 1.2.1 is loaded. Original memory configuration, core instruction files, models, channels, schedules and skills configuration matched the pre-upgrade snapshot. All three gateways returned HTTP 200; Harry's Discord probe passed.

Cleanup completed: five old test/recovery directories compressed and tar-compared before removing originals; the 7.4 GiB historical tar was compressed and its full uncompressed SHA-256 matched before the original was removed. The failed installation attempt was archived without disposable npm/tmp trees, retaining the full original installed packages in the fresh backup. Final test copies were removed after matching their tested runtime files to production. Live npm download caches cleared, plus 7,672,074,240 bytes of redundant download caches removed from recovery copies. Installed software, credentials, workspace files and recovery state retained.

Final disk: 104,693,542,912 bytes free (97.51 GiB), about 50% used. Fresh Mem0 recovery state was added during this work, so concurrent free-space differences are not a valid gross-cleanup measure. No reboot required. Only the eight Ubuntu vendor-phased packages remain deferred.
