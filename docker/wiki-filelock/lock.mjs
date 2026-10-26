import { spawn } from 'node:child_process';
import { constants } from 'node:fs';
import { mkdir, open, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// All generations must share this stable inode. Never unlink the lock file.
export async function acquireWikiLock(vault, timeoutSeconds = 300) {
  if (process.platform !== 'linux') throw new Error('Shared Wiki filelock requires Linux');
  if (!Number.isFinite(timeoutSeconds) || timeoutSeconds < 0 || timeoutSeconds > 3600) {
    throw new RangeError('Wiki lock timeout must be between 0 and 3600 seconds');
  }
  const directory = path.join(vault, '.openclaw-wiki');
  await mkdir(directory, { recursive: true });
  const filename = path.join(directory, 'zedbiz-mutation.flock');
  const handle = await open(filename,
    constants.O_CREAT | constants.O_RDWR | constants.O_NOFOLLOW | constants.O_NONBLOCK, 0o660);
  try {
    if (!(await handle.stat()).isFile()) throw new Error('Wiki lock path is not a regular file');
    await new Promise((resolve, reject) => {
      // FD 3 refers to the SAME open-file description held by the Node parent.
      // Python only acquires the native lock; it does not own its lifetime.
      const child = spawn('/usr/bin/python3', [
        '-I', '-B', fileURLToPath(new URL('./acquire-lock.py', import.meta.url)),
        '3', String(timeoutSeconds),
      ], { stdio: ['ignore', 'ignore', 'pipe', handle.fd] });
      let spawnError;
      let timedOut = false;
      let detail = '';
      const timer = setTimeout(() => {
        timedOut = true;
        child.kill('SIGKILL');
      }, (timeoutSeconds + 5) * 1000);
      child.stderr.on('data', chunk => { detail = (detail + chunk).slice(-1000); });
      child.once('error', error => { spawnError = error; });
      // Wait for close even on failure: no acquiring child may outlive cleanup.
      child.once('close', (code, signal) => {
        clearTimeout(timer);
        if (spawnError) reject(spawnError);
        else if (timedOut || code === 75) {
          reject(Object.assign(new Error('Timed out waiting for the shared Wiki lock'),
            { code: 'WIKI_LOCK_TIMEOUT' }));
        } else if (code !== 0) {
          reject(new Error(`Wiki filelock acquisition failed (${code ?? signal}): ${detail}`));
        } else resolve();
      });
    });
    const held = await handle.stat();
    const named = await stat(filename);
    if (held.nlink === 0 || held.dev !== named.dev || held.ino !== named.ino) {
      throw new Error('Wiki lock file changed during acquisition');
    }
  } catch (error) {
    await handle.close();
    throw error;
  }
  let release;
  return () => release ??= handle.close();
}
