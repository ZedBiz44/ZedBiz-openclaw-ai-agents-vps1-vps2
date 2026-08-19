# ZedBiz Remotion Video Template

Reusable vertical or horizontal video assembly for ZedBiz agents. It combines sequential color, image, or video scenes with narration, music, a logo, and crisp animated captions.

## Install

```bash
npm ci
```

## Verify

```bash
npm run typecheck
REMOTION_BROWSER_EXECUTABLE=/usr/bin/chromium npm run smoke
```

If system Chromium is unavailable, omit `REMOTION_BROWSER_EXECUTABLE` and allow Remotion to obtain its supported browser.

## Render A Project

```bash
npm run render -- projects/example.json outputs/example.mp4
```

Relative media paths resolve from the template's `public/` folder. HTTPS, data, and file URLs are accepted. Keep each production's source assets, configuration, proof renders, and final exports together.

## Project Fields

- `width`, `height`, and `fps` control output format.
- `scenes` contains sequential color, image, or video blocks with durations in frames.
- `captions` contains exact start and end frames plus visible text.
- `voiceoverSrc`, `musicSrc`, and `logoSrc` are optional media sources.
- Caption and branding colours can be changed without regenerating source footage.

## Rollback

Remove the deployed template directory or restore the preceding committed version. It does not modify provider media or agent configuration.
