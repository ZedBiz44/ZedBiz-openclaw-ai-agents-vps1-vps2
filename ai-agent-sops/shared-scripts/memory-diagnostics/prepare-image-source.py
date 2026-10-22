#!/usr/bin/env python3
"""Prepare only the verified OpenClaw 2026.9.8 module for the Amanda image."""
import hashlib
import pathlib
import sys
source=pathlib.Path(sys.argv[1]).read_bytes().replace(bytes([13,10]),bytes([10]))
expected="c305ab8b9e91a6c4ae4d2272ceb5ec14c05c98a5a04f5ba9e4a48b58b89ad06f"
if hashlib.sha256(source).hexdigest()!=expected:
    raise SystemExit("Source hash differs; review this build before patching")
text=source.decode()
old="options?.processMemoryLimitBytes ?? DEFAULT_PROCESS_MEMORY_LIMIT_BYTES"
assert text.count(old)==1
text=text.replace(old,"options?.processMemoryLimitBytes ?? process.constrainedMemory()")
text=text.replace("const DEFAULT_PROCESS_MEMORY_LIMIT_BYTES = process.constrainedMemory();"+chr(10),"")
output=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else pathlib.Path("diagnostic-kx61_Tco.mjs")
output.write_bytes(text.encode())
assert hashlib.sha256(output.read_bytes()).hexdigest()=="8470e0b89e9188b565a2ca708974959b1002b050651ef5d9a3cc06e119fbdd49"
print("Verified memory-limit patch prepared")
