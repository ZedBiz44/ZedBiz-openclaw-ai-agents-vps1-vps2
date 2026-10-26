#!/usr/bin/env node
/**
 * Offline behavior proof for the staged OpenClaw reconnect candidate.
 *
 * This runner never writes the native module tree. It hashes the native
 * original, imports the staged candidate from a data: URL, and rewrites that
 * candidate's static imports to file: URLs in the supplied native root. The
 * only HTTP permitted during the proof is the in-process 127.0.0.1 fixture.
 *
 * Local example after an approved dependency extraction:
 *   node run-native-behavior-proof.mjs --native-root /path/to/node_modules/openclaw \
 *     --candidate /home/ubuntu/reconnect-native-prep/candidate/vps2/frank/dist/agents/agent-bundle-mcp-runtime.js
 *
 * Native in-memory example (no remote files written): provide the runner on
 * stdin to Node and set NATIVE_ROOT plus CANDIDATE_SOURCE_B64 in its environment.
 */
import assert from "node:assert/strict";
import { createHash, randomUUID } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import http from "node:http";
import { createRequire } from "node:module";
import { basename, isAbsolute, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const EXPECTED_ORIGINAL_SHA256 = "1abddd912cab692e7e64105643f86f43d14b4fb0756bd1d3f32fe28b70dfc83d";
const EXPECTED_CANDIDATE_SHA256 = "bd6edaa247a62a902bd9c10e18e349580d3735d75f7ae8fd82597834ab5a5372";
const RUNTIME_RELATIVE_PATH = "dist/agents/agent-bundle-mcp-runtime.js";
const REQUEST_CONTEXT_RELATIVE_PATH = "dist/agent-bundle-mcp-request-context-905XWHsu.mjs";

function usage(exitCode = 0) {
  const text = `Usage: node ${basename(process.argv[1] ?? "run-native-behavior-proof.mjs")} --native-root <openclaw-root> [--candidate <candidate-module>]

Required input alternatives:
  --candidate <path>                    Read staged candidate from this local path.
  CANDIDATE_SOURCE_B64=<base64>          Read staged candidate from environment (for no-write native stdin use).

The candidate and native original must match the fixed expected SHA-256 values.
The runner writes no temporary files and permits only its own 127.0.0.1 fixture HTTP traffic.`;
  (exitCode === 0 ? console.log : console.error)(text);
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { nativeRoot: process.env.NATIVE_ROOT, candidate: process.env.CANDIDATE_PATH };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") usage(0);
    if (arg === "--native-root") args.nativeRoot = argv[++index];
    else if (arg === "--candidate") args.candidate = argv[++index];
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!args.nativeRoot) throw new Error("Missing --native-root or NATIVE_ROOT.");
  if (!isAbsolute(args.nativeRoot)) throw new Error("--native-root must be an absolute path.");
  if (args.candidate && !isAbsolute(args.candidate)) throw new Error("--candidate must be an absolute path.");
  return args;
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

async function loadCandidate(candidatePath) {
  if (process.env.CANDIDATE_SOURCE_B64) {
    const source = Buffer.from(process.env.CANDIDATE_SOURCE_B64, "base64").toString("utf8");
    if (!source) throw new Error("CANDIDATE_SOURCE_B64 decoded to an empty candidate.");
    return source;
  }
  if (!candidatePath) throw new Error("Provide --candidate or CANDIDATE_SOURCE_B64.");
  return readFile(candidatePath, "utf8");
}

/**
 * Convert static candidate imports to absolute native file URLs. Data URL
 * modules cannot resolve relative or package specifiers themselves. Transitive
 * imports continue to resolve normally from their real native file URLs.
 */
function rewriteStaticImports(candidateSource, nativeRuntimePath) {
  const nativeRuntimeUrl = pathToFileURL(nativeRuntimePath);
  const nativeRequire = createRequire(nativeRuntimePath);
  const resolveSpecifier = (specifier) => {
    if (specifier.startsWith("node:")) return specifier;
    if (specifier.startsWith(".") || specifier.startsWith("/")) {
      return new URL(specifier, nativeRuntimeUrl).href;
    }
    return pathToFileURL(nativeRequire.resolve(specifier)).href;
  };

  let replacementCount = 0;
  const rewritten = candidateSource.replace(/\b(from|import)\s*(["'])([^"']+)\2/g, (whole, keyword, quote, specifier) => {
    // Static imports are the only allowed rewritten locations. The candidate
    // has no dynamic import expressions in its module preamble.
    replacementCount += 1;
    return `${keyword} ${quote}${resolveSpecifier(specifier)}${quote}`;
  });
  if (replacementCount < 21) {
    throw new Error(`Expected at least 21 static imports in candidate, rewrote ${replacementCount}.`);
  }
  if (/\b(?:from|import)\s*["']\.\.?\//.test(rewritten)) {
    throw new Error("A relative candidate import remained after data-URL adaptation.");
  }
  return rewritten;
}

async function listenLoopback(server) {
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen);
    server.listen(0, "127.0.0.1", () => {
      server.off("error", rejectListen);
      resolveListen();
    });
  });
  const address = server.address();
  assert(address && typeof address === "object", "Fixture did not receive a TCP address.");
  return address.port;
}

function closeServer(server) {
  server.closeAllConnections();
  return new Promise((resolveClose, rejectClose) => server.close((error) => error ? rejectClose(error) : resolveClose()));
}

async function main() {
  const { nativeRoot, candidate: candidatePath } = parseArgs(process.argv.slice(2));
  const nativeRuntimePath = resolve(nativeRoot, RUNTIME_RELATIVE_PATH);
  const requestContextPath = resolve(nativeRoot, REQUEST_CONTEXT_RELATIVE_PATH);
  const [nativeSource, candidateSource] = await Promise.all([readFile(nativeRuntimePath, "utf8"), loadCandidate(candidatePath)]);
  await Promise.all([stat(requestContextPath), stat(nativeRuntimePath)]);

  const nativeOriginalSha256 = sha256(nativeSource);
  const candidateSha256 = sha256(candidateSource);
  assert.equal(nativeOriginalSha256, EXPECTED_ORIGINAL_SHA256, "Native runtime is not the asserted original hash.");
  assert.equal(candidateSha256, EXPECTED_CANDIDATE_SHA256, "Candidate is not the asserted staged candidate hash.");

  const rewrittenCandidate = rewriteStaticImports(candidateSource, nativeRuntimePath);
  const candidateDataUrl = `data:text/javascript;base64,${Buffer.from(rewrittenCandidate, "utf8").toString("base64")}#native-proof-${randomUUID()}`;
  const nativeRequire = createRequire(nativeRuntimePath);
  const clientModuleUrl = pathToFileURL(nativeRequire.resolve("@modelcontextprotocol/sdk/client/index.js")).href;
  const contextModuleUrl = pathToFileURL(requestContextPath).href;

  let expired = false;
  let toolFail = false;
  let slowLists = false;
  let connections = 0;
  let calls = 0;
  let capturedClient;
  const fixtureRequestMethods = [];
  const server = http.createServer(async (req, res) => {
    fixtureRequestMethods.push(req.method ?? "UNKNOWN");
    if (req.method === "GET") { res.writeHead(405); res.end(); return; }
    if (req.method === "DELETE") { res.writeHead(200); res.end(); return; }
    let body = "";
    for await (const chunk of req) body += chunk;
    let query;
    try { query = JSON.parse(body); } catch { res.writeHead(400); res.end(); return; }
    const send = (result, error) => {
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", id: query.id, ...(error ? { error } : { result }) }));
    };
    if (query.method === "initialize") {
      connections += 1;
      await new Promise((done) => setTimeout(done, 100));
      res.setHeader("mcp-session-id", `fixture-${connections}`);
      send({ protocolVersion: "2025-03-26", capabilities: { tools: {} }, serverInfo: { name: "fixture", version: "1" } });
      return;
    }
    if (query.method === "notifications/initialized") { res.writeHead(202); res.end(); return; }
    if (query.method === "tools/list") {
      if (slowLists) await new Promise((done) => setTimeout(done, 150));
      send({ tools: [{ name: "identity", description: "Fixture", inputSchema: { type: "object", properties: {} } }] });
      return;
    }
    if (query.method === "tools/call") {
      calls += 1;
      if (expired) {
        expired = false;
        res.writeHead(404, { "content-type": "application/json" });
        res.end(JSON.stringify({ jsonrpc: "2.0", id: query.id, error: { code: -32001, message: "Session not found" } }));
        return;
      }
      if (toolFail) { toolFail = false; send(null, { code: -32603, message: "fixture tool failure" }); return; }
      send({ content: [{ type: "text", text: "pass" }] });
      return;
    }
    res.writeHead(400); res.end();
  });

  const port = await listenLoopback(server);
  const expectedFixtureUrl = `http://127.0.0.1:${port}/mcp`;
  const originalFetch = globalThis.fetch;
  if (typeof originalFetch !== "function") throw new Error("Node global fetch is required for this fixture.");
  const outboundUrls = [];
  globalThis.fetch = async function loopbackOnlyFetch(input, init) {
    const rawUrl = input instanceof Request ? input.url : input instanceof URL ? input.href : String(input);
    const parsed = new URL(rawUrl);
    outboundUrls.push(parsed.href);
    if (parsed.protocol !== "http:" || parsed.hostname !== "127.0.0.1" || parsed.port !== String(port)) {
      throw new Error(`Blocked non-loopback network request: ${parsed.href}`);
    }
    return originalFetch.call(this, input, init);
  };

  let Client;
  let withSignal;
  let connect;
  let runtime;
  const passed = [];
  try {
    // Import the exact native aliases that the original fixture uses only
    // after the loopback-only fetch guard is installed. Importing Client via
    // the same resolved URL makes the prototype interception apply to the
    // client class instantiated by the data-URL candidate.
    const [clientModule, requestContext] = await Promise.all([import(clientModuleUrl), import(contextModuleUrl)]);
    Client = clientModule.Client;
    withSignal = requestContext.n;
    assert.equal(typeof Client, "function", "Native SDK Client export is unavailable.");
    assert.equal(typeof withSignal, "function", "Native request-context export n (withSignal) is unavailable.");
    connect = Client.prototype.connect;
    const candidateModule = await import(candidateDataUrl);
    const createSessionMcpRuntime = candidateModule.createSessionMcpRuntime;
    assert.equal(typeof createSessionMcpRuntime, "function", "Candidate did not export createSessionMcpRuntime.");

    Client.prototype.connect = async function interceptedConnect(...args) {
      capturedClient = this;
      return connect.apply(this, args);
    };
    const cfg = { mcp: { servers: { fixture: { transport: "streamable-http", url: expectedFixtureUrl } } } };
    runtime = createSessionMcpRuntime({ cfg, sessionId: "isolated-regression", sessionKey: "agent:main:main", workspaceDir: "/tmp", agentDir: "/tmp" });

    await runtime.getCatalog();
    await runtime.callTool("fixture", "identity", {});
    assert.equal(calls, 1);
    passed.push("connected call passes");

    expired = true;
    await assert.rejects(runtime.callTool("fixture", "identity", {}), /Session not found/);
    assert.equal(calls, 2);
    passed.push("expired tool request fails once without replay");

    await runtime.callTool("fixture", "identity", {});
    assert.equal(calls, 3);
    assert.equal(connections, 2);
    passed.push("next requested call awaits reconnect and executes once");

    toolFail = true;
    await assert.rejects(runtime.callTool("fixture", "identity", {}), /fixture tool failure/);
    await new Promise((done) => setTimeout(done, 150));
    assert.equal(calls, 4);
    passed.push("ordinary tool failure remains failed without replay");

    const signal = AbortSignal.abort(new Error("fixture cancellation"));
    await assert.rejects(withSignal(signal, () => runtime.callTool("fixture", "identity", {})), /fixture cancellation/);
    assert.equal(calls, 4);
    passed.push("already-aborted caller never dispatches");

    slowLists = true;
    expired = true;
    await assert.rejects(runtime.callTool("fixture", "identity", {}), /Session not found/);
    assert.equal(calls, 5);
    const first = runtime.callTool("fixture", "identity", {});
    await new Promise((done) => setTimeout(done, 130));
    const second = runtime.callTool("fixture", "identity", {});
    await Promise.all([first, second]);
    assert.equal(calls, 7);
    assert.equal(connections, 3);
    passed.push("parallel callers during slow reconnect catalog await full metadata and dispatch exactly once each");

    assert(capturedClient, "Fixture did not capture the native SDK Client.");
    await capturedClient.close();
    await runtime.callTool("fixture", "identity", {});
    assert.equal(calls, 8);
    assert.equal(connections, 4);
    passed.push("transport close awaits fresh connection before dispatch");

    assert(fixtureRequestMethods.length > 0, "Loopback fixture received no MCP HTTP request.");
    console.log(JSON.stringify({
      passed: passed.length,
      tests: passed,
      toolCalls: calls,
      connections,
      nativeRoot,
      nativeOriginalSha256,
      candidateSha256,
      withSignalExport: "n",
      syntheticMcpEndpoint: expectedFixtureUrl,
      loopbackFixtureRequestMethods: fixtureRequestMethods,
      globalFetchGuardInstalled: true,
      observedGlobalFetchUrls: [...new Set(outboundUrls)],
      noNativeModuleWrite: true,
      noLiveChange: true
    }, null, 2));
  } finally {
    if (Client && connect) Client.prototype.connect = connect;
    globalThis.fetch = originalFetch;
    await runtime?.dispose().catch(() => undefined);
    await closeServer(server).catch(() => undefined);
  }
}

main().catch((error) => {
  console.error(error?.stack ?? String(error));
  process.exitCode = 1;
});
