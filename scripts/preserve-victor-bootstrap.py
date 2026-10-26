import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
cfg = json.loads(path.read_text())
defaults = cfg.setdefault('agents', {}).setdefault('defaults', {})
old = defaults.get('bootstrapMaxChars', 20000)
defaults['bootstrapMaxChars'] = max(old, 24000)
path.write_text(json.dumps(cfg, indent=2)+'\n')
print(json.dumps({'bootstrapMaxCharsBefore':old,'bootstrapMaxCharsAfter':defaults['bootstrapMaxChars']}))
