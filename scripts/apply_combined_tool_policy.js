#!/usr/bin/env node
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const [configPath, agentsPath, policyPath, overridePath, backupRoot] = process.argv.slice(2);
if (![configPath, agentsPath, policyPath, overridePath, backupRoot].every(Boolean)) {
  throw new Error('Usage: apply_combined_tool_policy.js <config> <agents> <policy> <override> <backup-root>');
}

const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const backupDir = path.join(backupRoot, `combined-tool-policy-${stamp}`);
const configRaw = fs.readFileSync(configPath, 'utf8');
const agentsRaw = fs.readFileSync(agentsPath, 'utf8');
const policyRaw = fs.readFileSync(policyPath, 'utf8').trim();
const override = JSON.parse(fs.readFileSync(overridePath, 'utf8'));
const config = JSON.parse(configRaw);

const models = config?.agents?.defaults?.models;
if (!models) throw new Error('Missing agents.defaults.models');
let configChanged = false;
for (const [model, expected] of Object.entries(override.models)) {
  if (!models[model]?.agentRuntime?.id) throw new Error(`Missing runtime mapping for ${model}`);
  if (models[model].agentRuntime.id !== expected.agentRuntime.id) {
    models[model].agentRuntime.id = expected.agentRuntime.id;
    configChanged = true;
  }
}

const begin = '<!-- BEGIN ZEDBIZ COMBINED TOOL POLICY -->';
const end = '<!-- END ZEDBIZ COMBINED TOOL POLICY -->';
const block = `${begin}\n\n${policyRaw}\n\n${end}`;
const blockPattern = new RegExp(`${begin.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?${end.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'm');
const agentsNext = blockPattern.test(agentsRaw)
  ? agentsRaw.replace(blockPattern, block)
  : `${agentsRaw.trimEnd()}\n\n${block}\n`;
const agentsChanged = agentsNext !== agentsRaw;

if (configChanged || agentsChanged) {
  fs.mkdirSync(backupDir, { recursive: true, mode: 0o700 });
  fs.copyFileSync(configPath, path.join(backupDir, 'openclaw.json'));
  fs.copyFileSync(agentsPath, path.join(backupDir, 'AGENTS.md'));
  fs.writeFileSync(path.join(backupDir, 'before.json'), JSON.stringify({
    configSha256: hash(configRaw),
    agentsSha256: hash(agentsRaw),
    configMode: fs.statSync(configPath).mode & 0o777,
    agentsMode: fs.statSync(agentsPath).mode & 0o777,
  }, null, 2) + '\n', { mode: 0o600 });
}

if (configChanged) {
  const temp = `${configPath}.combined-tool-policy-${process.pid}`;
  fs.writeFileSync(temp, `${JSON.stringify(config, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(temp, configPath);
  fs.chmodSync(configPath, 0o600);
}
if (agentsChanged) {
  fs.writeFileSync(agentsPath, agentsNext, { mode: fs.statSync(agentsPath).mode & 0o777 });
}

const result = {
  configChanged,
  agentsChanged,
  backupDir: configChanged || agentsChanged ? backupDir : null,
  currentMappings: Object.fromEntries(Object.keys(override.models).map((model) => [model, models[model].agentRuntime.id])),
  policySha256: hash(policyRaw),
  policyPresent: agentsNext.includes(begin) && agentsNext.includes(end),
};
console.log(JSON.stringify(result));
