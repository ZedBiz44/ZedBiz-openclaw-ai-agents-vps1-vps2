#!/usr/bin/env node

import { GoogleGenAI } from "@google/genai";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import {
  DEFAULT_MODEL,
  buildPrompt,
  normalizeYoutubeUrl,
  safeUsage,
} from "./lib.mjs";

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  process.stderr.write("GEMINI_API_KEY is not available.\n");
  process.exit(1);
}

const model = process.env.GEMINI_VIDEO_MODEL || DEFAULT_MODEL;
const client = new GoogleGenAI({ apiKey });
const server = new McpServer({
  name: "z-gemini-video-mcp",
  version: "0.1.0",
});

server.registerTool(
  "analyze_youtube_video",
  {
    title: "Analyze a public YouTube video",
    description:
      "Watch one public YouTube video with Gemini and return audio, visual, timestamp, claim, and uncertainty details.",
    inputSchema: {
      youtube_url: z.string().describe("One public HTTPS YouTube URL."),
      question: z
        .string()
        .max(4000)
        .optional()
        .describe("Optional question or business purpose for the analysis."),
    },
  },
  async ({ youtube_url, question }) => {
    try {
      const safeUrl = normalizeYoutubeUrl(youtube_url);
      const interaction = await client.interactions.create({
        model,
        store: false,
        input: [
          { type: "text", text: buildPrompt(question) },
          { type: "video", uri: safeUrl },
        ],
      });

      const output = interaction.output_text?.trim();
      if (!output) {
        throw new Error("Gemini returned no text analysis.");
      }

      const result = {
        source: safeUrl,
        model,
        stored_by_interactions_api: false,
        usage: safeUsage(interaction),
        analysis: output,
      };

      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        isError: true,
        content: [{ type: "text", text: `Gemini video analysis failed: ${message}` }],
      };
    }
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
