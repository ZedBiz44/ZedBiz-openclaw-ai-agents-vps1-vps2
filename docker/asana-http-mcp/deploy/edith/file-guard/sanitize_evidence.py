"""Conservative output filter; never rewrites source documents or rotates secrets."""
import re

PATTERNS = [
    re.compile(r'(?i)password|passwd|secret.?key|api.?key|access.?token|refresh.?token|login credentials|username\s*:|authorization\s*:'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
    re.compile(r'\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_\-]{12,}\b'),
    re.compile(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'),
    re.compile(r'https?://[^\s/:]+:[^\s/@]+@'),
]


def suspected(text):
    return any(p.search(text) for p in PATTERNS)


def sanitize(text):
    # Withhold the entire excerpt if any indicator is present. Neighbor-only
    # redaction misses multiline credentials and values separated from labels.
    if suspected(text):
        return '[Excerpt withheld: possible credentials; restricted review required.]', True
    return text, False
