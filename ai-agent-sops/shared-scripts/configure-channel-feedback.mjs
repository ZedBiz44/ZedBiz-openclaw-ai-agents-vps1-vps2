#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const apply = args.includes("--apply");
const configPath = args.find((arg) => !arg.startsWith("--"));

if (!configPath) {
  console.error("Usage: configure-channel-feedback.mjs <openclaw.json> [--apply]");
  process.exit(2);
}

const supportedChannels = new Set(["discord", "telegram", "slack"]);
const originalText = fs.readFileSync(configPath, "utf8");
const config = JSON.parse(originalText);
const configuredChannels = Object.keys(config.channels ?? {}).filter((channel) =>
  supportedChannels.has(channel),
);

if (configuredChannels.length === 0) {
  console.error("No configured Discord, Telegram, or Slack channels were found.");
  process.exit(3);
}

config.messages = {
  ...(config.messages ?? {}),
  ackReactionScope: "all",
  removeAckAfterReply: true,
};

for (const channel of configuredChannels) {
  const current = config.channels[channel] ?? {};
  config.channels[channel] = {
    ...current,
    ackReaction: channel === "slack" ? "eyes" : "\u{1F440}",
    streaming: {
      ...(typeof current.streaming === "object" && current.streaming !== null
        ? current.streaming
        : {}),
      mode: "progress",
      progress: {
        ...(typeof current.streaming?.progress === "object" &&
        current.streaming.progress !== null
          ? current.streaming.progress
          : {}),
        label: "Working",
        toolProgress: true,
        commandText: "status",
      },
    },
  };
}

const summary = {
  configPath,
  mode: apply ? "apply" : "dry-run",
  acknowledgementScope: config.messages.ackReactionScope,
  removeAcknowledgementAfterReply: config.messages.removeAckAfterReply,
  channels: Object.fromEntries(
    configuredChannels.map((channel) => [
      channel,
      {
        acknowledgement: config.channels[channel].ackReaction,
        streamingMode: config.channels[channel].streaming.mode,
        progressLabel: config.channels[channel].streaming.progress.label,
        toolProgress: config.channels[channel].streaming.progress.toolProgress,
        commandText: config.channels[channel].streaming.progress.commandText,
      },
    ]),
  ),
};

if (!apply) {
  console.log(JSON.stringify(summary, null, 2));
  process.exit(0);
}

const stamp = new Date().toISOString().replaceAll(":", "").replaceAll(".", "");
const backupPath = `${configPath}.bak-channel-feedback-${stamp}`;
const tempPath = path.join(
  path.dirname(configPath),
  `.${path.basename(configPath)}.channel-feedback-${process.pid}.tmp`,
);
const mode = fs.statSync(configPath).mode;

fs.copyFileSync(configPath, backupPath, fs.constants.COPYFILE_EXCL);
fs.writeFileSync(tempPath, `${JSON.stringify(config, null, 2)}\n`, {
  encoding: "utf8",
  mode,
});
fs.renameSync(tempPath, configPath);

console.log(JSON.stringify({ ...summary, backupPath }, null, 2));
