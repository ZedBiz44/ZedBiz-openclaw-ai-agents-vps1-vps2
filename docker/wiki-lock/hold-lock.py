"""Hold a Linux flock until the requesting Node process closes its stdin."""
import fcntl
import os
import sys
import time

path, timeout = sys.argv[1], float(sys.argv[2])
fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o660)
deadline = time.monotonic() + timeout
while True:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
    except BlockingIOError:
        if time.monotonic() >= deadline:
            raise SystemExit(75)
        time.sleep(0.05)
print('locked', flush=True)
# EOF also releases the lock if the requesting process crashes. Never unlink
# this file: replacing its inode would allow two independent lock owners.
sys.stdin.buffer.read()
os.close(fd)
