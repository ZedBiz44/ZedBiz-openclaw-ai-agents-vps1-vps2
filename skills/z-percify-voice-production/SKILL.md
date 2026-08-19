---
name: z-percify-voice-production
description: Create approved narration or speaking-avatar audio through Percify when a ZedBiz video needs a consistent stock or cloned voice.
---

# ZedBiz Percify Voice Production

Use Percify as the primary voice provider for ZedBiz video production. Create the approved master narration before avatar, caption, or assembly work begins.

## Required Inputs

- Final approved script
- Project name and output folder
- Voice choice: saved avatar, approved reference audio, or approved stock voice
- Language and pronunciation notes
- Whether the output is narration-only or a speaking-avatar clip
- Maximum approved credit cost

Do not generate from a draft script. Do not clone a voice unless the speaker's permission is recorded in the project brief.

## Connection Check

- Confirm the `percify` MCP server is available.
- Call `list_models` or `list_avatars` before treating the connection as working.
- If Percify is unavailable, report the missing connection or credential. Do not silently switch providers.
- Never print, store, or paste the API key into project files, prompts, logs, or this skill.

## Choose The Voice Route

- Use a saved Percify Avatar Persona and `avatar_say` for a recurring speaking character.
- Use Zonos 2 or XTTS-v2 with approved reference audio for cloned narration without an avatar.
- Use an approved stock TTS voice when voice cloning is unnecessary.
- Use ElevenLabs directly only when Jack has approved that fallback and its separate account connection is ready.

Read [Percify voice workflows](references/percify-voice-workflows.md) for the exact tool sequence and model-selection rules.

## Production Workflow

- Save the approved script and voice instructions before generating.
- Call `get_model` for the chosen model and validate its required inputs.
- Call `estimate_cost` before every credit-spending generation.
- Stop for approval when the estimate exceeds the project limit or no limit was supplied for a production-length job.
- Call `generate` for narration or `avatar_say` for a saved speaking avatar.
- Monitor with `wait_for_generation` or `get_avatar_job`; do not flood the provider with rapid polling.
- Download the completed media into the project folder.
- Record provider, model, job ID, credit estimate, actual credits when available, voice identity, script version, and output path.
- Listen to the entire result before marking it approved.

## Quality Check

- Confirm every script word is present and in the correct order.
- Check pronunciation, pacing, pauses, emotion, volume, noise, and clipping.
- Confirm the voice identity stays consistent from beginning to end.
- Reject fabricated words, truncated sentences, unexplained voice changes, or unusable audio artifacts.
- Regenerate only the failed segment when the project uses scene audio; do not replace approved segments unnecessarily.

## Output Layout

Store voice assets under the active video project:

- `audio/master-narration.*`
- `audio/scenes/scene-###.*`
- `audio/references/` for approved source samples
- `records/voice-generation.json` for provider and job details

Do not overwrite an approved master. Save revisions with a new version and identify the currently approved file in the project record.

## Failure And Fallback

- Retry one transient provider failure after the documented wait interval.
- If a generation fails twice, preserve the job IDs and error details and stop.
- If cloning quality fails, test the other approved Percify cloning model before recommending ElevenLabs.
- If Percify is unavailable and the project can use a stock voice, offer the configured stock-voice route; do not switch automatically.
- Never submit the same paid job repeatedly merely because status polling is slow.

## Completion Evidence

Report:

- Approved output file
- Provider and model
- Voice or avatar used
- Job ID
- Estimated and actual credit use when available
- Script version
- Quality-control result
