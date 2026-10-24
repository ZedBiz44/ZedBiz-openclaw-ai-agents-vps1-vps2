# VPS1 Asana component build

This source preserves the deployed Amanda recovery service, including Standard and Advanced entrypoints. It updates Node to 24.22.0 and refreshes the locked SDK/HTTP dependencies. The standard entrypoint exposes 76 tools; `dist/advanced-server.js` exposes 126. Existing Compose commands choose the entrypoint.

`Dockerfile` builds `zedbiz/asana-http-mcp:2.0.0-components-20261018`. `Dockerfile.edith` uses the same tree with `variants/edith/asana-client-wrapper.ts` overlaid before compilation, preserving Edith's all-pages task retrieval and cursor/error guards. It builds `zedbiz/asana-http-mcp:2.0.0-edith-components-20261018`.

Both builds run typecheck, build, tool-catalog checks and a production dependency audit. Authenticated isolated tests compared each variant's catalog and own-user identity against its previous live service. Edith's targeted test covered combined pages, preserved query fields, repeated cursor rejection and invalid-page rejection. The deployed source was collected from the verified candidate directories; credentials and runtime captures are excluded.

The dated deployment record and protected host receipts contain image IDs, recovery archive checksums and live results. Operational procedures are maintained in Notion.
