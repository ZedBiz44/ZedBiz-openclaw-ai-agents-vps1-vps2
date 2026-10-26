#!/usr/bin/env python3
"""Patch OpenClaw 2026.10.4 Workshop empty-collection handling in a derived image."""
from pathlib import Path
import sys
p=Path(sys.argv[1])
old=p.read_text()
needle='"Work only in this directory. Shell commands follow the operator\'s existing automation approval policy.",'
addition='\n\t"The assigned directory is already the listing tool current working directory. Call ls with an empty arguments object {} (openclaw__ls({}) in code mode); do not ask for a path or invent an absolute path. If the complete listing is empty, finish successfully with: No Workshop skills to review; no changes needed. Do not list any wider workspace, parent directory, another agent, or installed skills to fill an empty collection. Empty is a valid completed review.",'
if addition in old:
    print('already patched')
else:
    if old.count(needle)!=1:
        raise SystemExit('Unexpected upstream module; inspect before patching')
    p.write_text(old.replace(needle,needle+addition))
    print('patched')
