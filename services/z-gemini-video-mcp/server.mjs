#!/usr/bin/env node

import { GoogleGenAI } from "@google/genai";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { analyzeMedia } from './media.mjs';

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
const client = new GoogleGenAI({ apiKey, httpOptions: {retryOptions:{attempts:1}} });
const server = new McpServer({
  name: "z-gemini-video-mcp",
  version: "0.2.0",
});

server.registerTool(
  "analyze_youtube_video",
  {
    title: "Analyze a public YouTube video",
    description:
      "Watch one public YouTube video with Gemini and return audio, visual, timestamp, claim, and uncertainty details.",
    annotations: {readOnlyHint:true,destructiveHint:false,idempotentHint:false,openWorldHint:true},
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

server.registerTool('analyze_media_file', {
  title:'Analyze a video or audio file',
  description:'Send an authorized local video/audio file to Gemini for actual sound and picture analysis. Use this for finished MP4 reviews, narration, music, transitions and targeted motion checks. The path must exist in this agent runtime. Consumes Gemini API usage. Temporary upload is deleted after analysis; no automatic retries. Sampling is not continuous playback.',
  annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:false,openWorldHint:true},
  inputSchema:{file_path:z.string().describe('Absolute path to the authorized video/audio file accessible in this runtime, at most 500 MiB.'),question:z.string().max(4000).optional(),fps:z.number().min(0.1).max(24).default(4).describe('Video frames sampled per second. Use 12-24 on short intervals for motion; does not guarantee precise lip-sync.'),start_seconds:z.number().min(0).optional(),end_seconds:z.number().positive().optional()}
}, async args => {
  try { return {content:[{type:'text',text:JSON.stringify(await analyzeMedia(client,model,args),null,2)}]}; }
  catch(e) { return {isError:true,content:[{type:'text',text:`Gemini media analysis failed: ${e.message}`} ]}; }
});

const transport = new StdioServerTransport();
await server.connect(transport);
