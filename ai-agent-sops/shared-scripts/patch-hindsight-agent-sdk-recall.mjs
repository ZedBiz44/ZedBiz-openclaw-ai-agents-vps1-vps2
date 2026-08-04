import fs from "node:fs";

const target = process.argv[2];

if (!target) {
  throw new Error("Usage: node patch-hindsight-agent-sdk-recall.mjs <agent-sdk-dist-index.js>");
}

const original = `            async execute(params) {
                const result = await client.recall(bankId, params.query, {
                    maxTokens: params.max_results ?? 10,
                });
                return ok(result);
            },`;

const replacement = `            async execute(params) {
                const maxResults = Math.max(1, Math.min(params.max_results ?? 10, 50));
                const result = await client.recall(bankId, params.query, {
                    maxTokens: 1024,
                });
                return ok({
                    ...result,
                    results: Array.isArray(result?.results) ? result.results.slice(0, maxResults) : result?.results,
                });
            },`;

const source = fs.readFileSync(target, "utf8");

if (source.includes(replacement)) {
  console.log(`Already patched: ${target}`);
  process.exit(0);
}

if (!source.includes(original)) {
  throw new Error(`Expected Hindsight recall block was not found: ${target}`);
}

fs.writeFileSync(target, source.replace(original, replacement));
console.log(`Patched: ${target}`);
