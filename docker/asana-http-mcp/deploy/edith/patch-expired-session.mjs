// Narrow compatibility patch for the deployed standard 2.0.0 bundle.
// Preserve its tool catalog and permissions; fail closed if the source differs.
import fs from 'node:fs';
const file = process.argv[2] ?? '/app/dist/index.js';
let text = fs.readFileSync(file, 'utf8');
const post = 'res.status(400).json({\n          jsonrpc:';
const other = 'res.status(400).send("Invalid or missing MCP session")';
if (text.split(post).length !== 2 || text.split(other).length !== 3) {
  throw new Error('Unexpected bundle; refuse to patch');
}
text = text.replace(post, 'res.status(sessionId ? 404 : 400).json({\n          jsonrpc:')
  .replaceAll(other, 'res.status(sessionId ? 404 : 400).send("Invalid or missing MCP session")');
fs.writeFileSync(file, text);
console.log('Patched only three expired-session HTTP responses');
