"""Acquire through maintained filelock; the Node writer retains descriptor ownership."""
import math
import os
import pathlib
import stat
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'vendor'))
import filelock

if filelock.__version__ != '4.2.1' or not filelock.has_fcntl:
    raise SystemExit('Expected native Linux filelock 4.2.1')
fd, timeout = int(sys.argv[1]), float(sys.argv[2])
if fd != 3 or not math.isfinite(timeout) or not 0 <= timeout <= 3600:
    raise SystemExit('Invalid descriptor or timeout')
if not stat.S_ISREG(os.fstat(fd).st_mode):
    raise SystemExit('Lock descriptor must be a regular file')
deadline = time.monotonic() + timeout
while not filelock.lock_descriptor(fd, blocking=False):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise SystemExit(75)
    time.sleep(min(0.05, remaining))
# No unlock_descriptor and no FileLock context manager here: either would
# explicitly unlock the parent's descriptor too. Process exit closes only this
# duplicate; Node retains the native lock until its own FileHandle is closed.
