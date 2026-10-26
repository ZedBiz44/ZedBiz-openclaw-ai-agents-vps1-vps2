"""Offline installation of the unmodified, pinned official wheel."""
import hashlib
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
WHEEL = ROOT / 'filelock-4.2.1-py3-none-any.whl'
SHA256 = '7be2662e9e826b9bba28afc0f843a123280d799a2ea44bb5d35ccec67905ae44'
if sys.version_info < (3, 11):
    raise SystemExit('filelock 4.2.1 requires Python >=3.11')
if hashlib.sha256(WHEEL.read_bytes()).hexdigest() != SHA256:
    raise SystemExit('Official filelock wheel checksum mismatch')
target = ROOT / 'vendor'
target.mkdir(exist_ok=False)
with zipfile.ZipFile(WHEEL) as archive:
    for name in archive.namelist():
        p = pathlib.PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or p.parts[0] not in ['filelock', 'filelock-4.2.1.dist-info']:
            raise SystemExit('Unexpected wheel entry')
    archive.extractall(target)
sys.path.insert(0, str(target))
import filelock
assert filelock.__version__ == '4.2.1' and filelock.has_fcntl
print('Installed unmodified filelock 4.2.1; official wheel SHA256 verified')
