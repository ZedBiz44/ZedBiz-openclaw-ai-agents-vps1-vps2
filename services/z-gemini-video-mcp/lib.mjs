const YOUTUBE_HOSTS = new Set([
  "youtube.com",
  "www.youtube.com",
  "m.youtube.com",
  "youtu.be",
]);

export const DEFAULT_MODEL = "gemini-3.8-flash";

export const DEFAULT_ANALYSIS_PROMPT = `Analyze the full public YouTube video.

Return these sections:
- Plain-language summary
- Step-by-step instructions or main points
- What is visible on screen, with useful timestamps
- What the presenter says or claims, with useful timestamps
- Differences between what is said and what is visibly shown
- Useful ideas or actions for ZedBiz
- Uncertain or missing details

Clearly separate direct observations from presenter claims. Do not describe a claim as independently verified unless another reliable source was actually checked.`;

export function normalizeYoutubeUrl(value) {
  if (typeof value !== "string" || value.length > 500) {
    throw new Error("Provide one public YouTube URL under 500 characters.");
  }

  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("Provide a valid public YouTube URL.");
  }

  if (url.protocol !== "https:" || !YOUTUBE_HOSTS.has(url.hostname.toLowerCase())) {
    throw new Error("Only public HTTPS YouTube URLs are allowed by this tool.");
  }

  if (url.username || url.password) {
    throw new Error("YouTube URLs containing credentials are not allowed.");
  }

  return url.toString();
}

export function buildPrompt(question) {
  if (question == null || question.trim() === "") {
    return DEFAULT_ANALYSIS_PROMPT;
  }

  const cleaned = question.trim();
  if (cleaned.length > 4000) {
    throw new Error("The analysis request must be 4,000 characters or fewer.");
  }

  return `${DEFAULT_ANALYSIS_PROMPT}\n\nJack's specific request:\n${cleaned}`;
}

export function safeUsage(interaction) {
  const usage = interaction?.usage ?? interaction?.usage_metadata ?? interaction?.usageMetadata;
  if (!usage || typeof usage !== "object") return null;

  return JSON.parse(JSON.stringify(usage));
}
