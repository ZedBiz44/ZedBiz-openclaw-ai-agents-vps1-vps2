import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const packageRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);

test("MCP server lists the tool and rejects an unsupported URL before any API call", async () => {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [path.join(packageRoot, "server.mjs")],
    cwd: packageRoot,
    env: {
      ...process.env,
      GEMINI_API_KEY: "safe-test-placeholder",
    },
  });
  const client = new Client({ name: "z-gemini-video-test", version: "0.1.0" });

  try {
    await client.connect(transport);
    const listed = await client.listTools();
    assert.deepEqual(
      listed.tools.map((tool) => tool.name),
      ["analyze_youtube_video"],
    );
    assert.deepEqual(listed.tools[0].annotations, {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: false,
      openWorldHint: true,
    });

    const result = await client.callTool({
      name: "analyze_youtube_video",
      arguments: { youtube_url: "https://example.com/not-youtube" },
    });
    assert.equal(result.isError, true);
    assert.match(result.content[0].text, /Only public HTTPS YouTube URLs/);
  } finally {
    await client.close();
  }
});
