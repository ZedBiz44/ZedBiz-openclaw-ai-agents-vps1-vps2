import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';

export async function acquireWikiLock(vault, timeoutSeconds = 300) {
  const directory = path.join(vault, '.openclaw-wiki');
  await mkdir(directory, { recursive: true });
  const child = spawn('/usr/bin/python3', [
    new URL('./hold-lock.py', import.meta.url).pathname,
    path.join(directory, 'zedbiz-mutation.flock'), String(timeoutSeconds),
  ], { stdio: ['pipe', 'pipe', 'pipe'] });
  // Handle EPIPE when startup/timeout fails before the release request.
  child.stdin.on('error', () => {});
  let releasing = false;
  let exited = false;
  let failure;
  let ready = false;
  let received = '';
  let errorText = '';
  child.stderr.on('data', chunk => { errorText = (errorText + chunk).slice(-1000); });
  const closed = new Promise(resolve => child.once('close', (code, signal) => {
    exited = true;
    if (!releasing) failure = new Error(`Wiki lock holder stopped (${code ?? signal}): ${errorText}`);
    resolve();
  }));
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      child.kill('SIGKILL');
      reject(new Error('Timed out waiting for the shared Wiki lock'));
    }, (timeoutSeconds + 5) * 1000);
    child.once('error', error => { clearTimeout(timer); reject(error); });
    child.once('close', () => {
      clearTimeout(timer);
      if (!ready) reject(failure ?? new Error('Wiki lock closed before acquisition'));
    });
    child.stdout.on('data', chunk => {
      received += chunk;
      if (received === 'locked\n') {
        ready = true;
        clearTimeout(timer);
        resolve();
      }
    });
  });
  return async () => {
    releasing = true;
    child.stdin.end();
    if (!exited) await closed;
    if (failure) throw failure;
  };
}
