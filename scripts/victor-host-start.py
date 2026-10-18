#!/usr/bin/python3
"""Victor boot recovery. Docker retains ownership of runtime crash restarts."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

MANIFEST = Path('/opt/openclaw/recovery/victor-20261018/manifest.json')


def log(message):
    print('victor-host-start: ' + message, flush=True)


def command(args, timeout=30, cwd=None):
    # Never forward wrapper/Compose output: credential tools can include secrets.
    proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
        raise RuntimeError('command timed out; no automatic retry of uncertain operation')
    return proc.returncode, out.decode('utf-8', errors='replace')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def recover(manifest, run=command):
    expected = {i['ref']: i['id'] for i in manifest['images'] if i['automatic']}
    wrapper = Path(manifest['wrapper'])
    if digest(wrapper) != manifest['wrapper_sha256']:
        raise RuntimeError('startup wrapper differs from approved manifest')
    rc, output = run(['/usr/bin/docker', 'compose', '--env-file', '.env',
                      'config', '--images'], cwd=str(wrapper.parent))
    if rc or set(output.split()) != set(expected):
        raise RuntimeError('declared Compose images differ from approved manifest')
    rc, _ = run(['/usr/bin/docker', 'info', '--format', '{{.ServerVersion}}'])
    if rc:
        raise RuntimeError('Docker daemon unavailable')
    missing = []
    for ref, image_id in expected.items():
        rc, output = run(['/usr/bin/docker', 'image', 'inspect', '--format', '{{.Id}}', ref])
        if rc:
            missing.append(ref)
        elif output.strip() != image_id:
            raise RuntimeError('selected image identity changed; refusing replacement')
    if missing:
        if digest(manifest['archive']) != manifest['sha256']:
            raise RuntimeError('image archive checksum failed')
        log('restoring approved missing images from verified local archive')
        rc, _ = run(['/usr/bin/docker', 'image', 'load', '--input', manifest['archive']], timeout=600)
        if rc:
            raise RuntimeError('image archive load failed')
        for ref, image_id in expected.items():
            rc, output = run(['/usr/bin/docker', 'image', 'inspect', '--format', '{{.Id}}', ref])
            if rc or output.strip() != image_id:
                raise RuntimeError('restored image identity failed verification')
    log('approved gateway and Asana images verified')


def start(manifest, run=command, pause=time.sleep):
    recover(manifest, run)
    for attempt in range(1, 4):
        log(f'startup attempt {attempt}/3')
        rc, _ = run([manifest['wrapper'], 'up'], timeout=180)
        if rc == 0:
            log('startup command succeeded; application health checked separately')
            return 0
        log(f'startup command failed with exit code {rc}')
        if attempt < 3:
            pause(30)
    log('three startup attempts exhausted; operator review required')
    return 1


def main():
    if len(sys.argv) != 1:
        raise RuntimeError('unexpected arguments')
    with open('/run/lock/victor-host-start.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return start(json.loads(MANIFEST.read_text()))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        # Known errors contain only fixed text; never print arbitrary exception data.
        log(str(exc) if isinstance(exc, RuntimeError) else 'preflight failed: ' + type(exc).__name__)
        sys.exit(1)
