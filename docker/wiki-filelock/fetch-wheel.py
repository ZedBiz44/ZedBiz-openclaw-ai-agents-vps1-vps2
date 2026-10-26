"""Fetch the exact official wheel; builds themselves run with no network."""
import hashlib,pathlib,urllib.request
root=pathlib.Path(__file__).resolve().parent
url='https://files.pythonhosted.org/packages/28/00/db89d339bc4ecdc8087fa7b8607ba22ffc27bf96286f340c9620bea428b3/filelock-4.2.1-py3-none-any.whl'
data=urllib.request.urlopen(url,timeout=60).read()
assert hashlib.sha256(data).hexdigest()=='7be2662e9e826b9bba28afc0f843a123280d799a2ea44bb5d35ccec67905ae44'
(root/'filelock-4.2.1-py3-none-any.whl').write_bytes(data)
print('Official wheel checksum verified')
