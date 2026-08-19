# Percify Voice Workflows

## Narration With A Cloned Voice

- Prefer `zonos2` when a clean approved reference recording is available. Supply the script as `text`, the reference as `audio`, and enable background cleanup only when the reference requires it.
- Use `xtts-v2` when its supported language and speaker input are a better match. Supply `text`, `speaker`, `language`, and the approved cleanup setting.
- Inspect the live schema with `get_model` before submitting because provider fields may change.
- Estimate cost, generate, wait for completion, download the audio, and run the full quality check.

## Narration With A Stock Voice

- Use a Percify text-to-speech model with a named voice, such as Qwen TTS Flash, only after listening to and approving that voice for the project.
- Record the exact model and voice name so later scenes use the same identity.
- Do not mix stock voices within one video unless the script deliberately contains multiple speakers.

## Saved Speaking Avatar

- Call `create_avatar` once with a clear approved face image and 10–30 seconds of clean approved voice audio.
- Give the avatar a stable business-readable name.
- Record the returned avatar ID in the character consistency package.
- Call `avatar_say` with that saved avatar, the approved script segment, and the approved quality level.
- Poll with `get_avatar_job` at sensible intervals until the job succeeds or fails.
- Download both the resulting video and any reusable audio output Percify exposes.

## Cost Controls

- Use `estimate_cost` before `generate` whenever the tool is available.
- Treat quality, resolution, audio duration, and model choice as cost controls.
- For an exploratory test, stop when the estimate exceeds 60 credits unless Jack supplied another limit.
- For production, use the limit recorded in the master brief.
- A failed generation should not be resubmitted until its final status is known.

## Provider Boundary

Percify is the provider connection. The skill controls how the agent uses it; the skill does not contain the API key or perform rendering itself.
