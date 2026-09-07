import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_ANALYSIS_PROMPT,
  buildPrompt,
  normalizeYoutubeUrl,
  safeUsage,
} from "../lib.mjs";

test("accepts normal public YouTube URLs", () => {
  assert.equal(
    normalizeYoutubeUrl("https://www.youtube.com/watch?v=eylReF4JPT0"),
    "https://www.youtube.com/watch?v=eylReF4JPT0",
  );
  assert.equal(
    normalizeYoutubeUrl("https://youtu.be/eylReF4JPT0"),
    "https://youtu.be/eylReF4JPT0",
  );
});

test("rejects non-YouTube and non-HTTPS URLs", () => {
  assert.throws(() => normalizeYoutubeUrl("https://example.com/video"));
  assert.throws(() => normalizeYoutubeUrl("http://youtube.com/watch?v=test"));
});

test("adds a specific request without dropping the standard checks", () => {
  const prompt = buildPrompt("Focus on the setup steps.");
  assert.match(prompt, /direct observations/i);
  assert.match(prompt, /Focus on the setup steps/);
  assert.ok(prompt.startsWith(DEFAULT_ANALYSIS_PROMPT));
});

test("uses the standard prompt when no question is supplied", () => {
  assert.equal(buildPrompt(), DEFAULT_ANALYSIS_PROMPT);
});

test("copies usage metadata without including the whole response", () => {
  assert.deepEqual(safeUsage({ usage: { totalTokens: 123 } }), {
    totalTokens: 123,
  });
  assert.equal(safeUsage({}), null);
});
