"""Retain the approved shared/derivative and sidecar artifacts outside Docker."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('/opt/openclaw/recovery/fleet-20261018')
root.mkdir(mode=0o700)
refs = [
    'zedbiz/openclaw-base:2026.10.4-fleet-20261018',
    'zedbiz/marsha:2026.10.4-fleet-20261018',
    'zedbiz/asana-http-mcp:2.0.0-standard',
    'zedbiz/asana-http-mcp:2.0.0-advanced',
    'zedbiz/asana-http-mcp:2.0.0-standard-edith-pagination-20260917',
    'zedbiz/openclaw-base:2026.9.8-terry-20261003-imapfix',
    'zedbiz/marsha:2026.9.8-owner-scheduling-20261003',
]
images = [dict(ref=ref, id=subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', ref], text=True).strip()) for ref in refs]
archive = root/'images.tar'
subprocess.run(['docker', 'image', 'save', '-o', str(archive)]+refs, check=True, timeout=600)
archive.chmod(0o600)
with archive.open('rb') as stream:
    checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
catalog = dict(archive=str(archive), sha256=checksum, images=images)
(root/'catalog.json').write_text(json.dumps(catalog, indent=2)); (root/'catalog.json').chmod(0o600)
print(json.dumps(dict(archiveBytes=archive.stat().st_size, **catalog)), flush=True)

