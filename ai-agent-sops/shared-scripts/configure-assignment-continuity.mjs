#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const target = process.argv[2];

if (!target) {
  console.error("Usage: configure-assignment-continuity.mjs <AGENTS.md>");
  process.exit(2);
}

const startMarker = "<!-- zedbiz-assignment-continuity:start -->";
const endMarker = "<!-- zedbiz-assignment-continuity:end -->";
const canonicalBlock = `${startMarker}
- Rely on the platform acknowledgement reaction for immediate receipt. Do not send a separate "I'm on it" acknowledgement message.
- Begin the assignment immediately. Send a written progress update only after substantive work has started, and always continue the same assignment after sending it.
- Let the platform manage its configured acknowledgement reaction; do not duplicate it with a manual reaction or empty text reply.
${endMarker}`;

const original = fs.readFileSync(target, "utf8");
const newline = original.includes("\r\n") ? "\r\n" : "\n";
let text = original.replace(/\r\n/g, "\n");

// Remove an earlier managed block and the fleet's known conflicting or partial
// acknowledgement rules. The durable knowledge-record wording about storing
// "empty acknowledgements" is intentionally not matched here.
text = text.replace(
  /<!-- zedbiz-assignment-continuity:start -->[\s\S]*?<!-- zedbiz-assignment-continuity:end -->\n*/g,
  "",
);

const obsoleteRules = [
  /^- Rely on the platform acknowledgement reaction for immediate receipt\..*$/gm,
  /^- Begin the assignment immediately\. Send a written progress update only after substantive work has started, and always continue the same assignment after sending it\.$/gm,
  /^- Let the platform manage its configured acknowledgement reaction;.*$/gm,
  /^- Acknowledge (?:Jack(?:'s)? )?(?:meaningful )?assignments? immediately\..*$/gm,
  /^- Acknowledge Jack's assignment immediately\..*$/gm,
  /^- Start assignments immediately\. In Discord or Slack, use non-terminal commentary for progress and reserve the `message` tool for the final user-visible response\..*$/gm,
  /^- Use the `message` tool directly for every Telegram reply;.*$/gm,
  /^- In Discord or Slack, one natural emoji reaction may replace an unnecessary acknowledgement\..*$/gm,
  /^- On Discord or Slack, a single natural emoji reaction may replace a text acknowledgement when appropriate;.*$/gm,
  /^- On Discord or Slack, a single natural reaction may replace a text-only acknowledgement when appropriate\.$/gm,
  /^- On Discord or Slack, a single natural emoji reaction may replace a text-only acknowledgement when no substantive response is needed\.$/gm,
  /^- Use at most one natural emoji reaction for simple Discord or Slack acknowledgement when a text response adds no value\.$/gm,
  /^- \*\*Action:\*\* Use natural emoji reactions \([^\n]*\) on Discord and Slack to acknowledge[^\n]*$/gm,
  /^- Routine updates state what changed, what it means, and what happens next\. Use one relevant reaction instead of a text acknowledgement where channel norms support it\.$/gm,
];

for (const pattern of obsoleteRules) {
  text = text.replace(pattern, "");
}

text = text.replace(/\n{3,}/g, "\n\n").trimEnd();

const communicationHeading = /^## (?:Communication[^\n]*)$/m;
const headingMatch = communicationHeading.exec(text);

if (headingMatch) {
  const insertAt = headingMatch.index + headingMatch[0].length;
  text = `${text.slice(0, insertAt)}\n\n${canonicalBlock}${text.slice(insertAt)}`;
} else {
  const firstSection = /^## /m.exec(text);
  const insertAt = firstSection?.index ?? text.length;
  const prefix = text.slice(0, insertAt).trimEnd();
  const suffix = text.slice(insertAt).trimStart();
  text = `${prefix}\n\n## Assignment Continuity\n\n${canonicalBlock}\n\n${suffix}`;
}

text = `${text.replace(/\n{3,}/g, "\n\n").trimEnd()}\n`;

const stamp = new Date().toISOString().replace(/[:.]/g, "");
const backup = `${target}.bak-assignment-continuity-${stamp}`;
fs.copyFileSync(target, backup);
fs.writeFileSync(target, text.replace(/\n/g, newline), "utf8");

const managedCount = (text.match(/zedbiz-assignment-continuity:start/g) ?? []).length;
const unsafeCount = (text.match(/^- Acknowledge .* immediately\./gm) ?? []).length;

if (managedCount !== 1 || unsafeCount !== 0) {
  fs.copyFileSync(backup, target);
  console.error(
    JSON.stringify({ target, backup, managedCount, unsafeCount, rolledBack: true }),
  );
  process.exit(1);
}

console.log(
  JSON.stringify({ target: path.resolve(target), backup, managedCount, unsafeCount }),
);
