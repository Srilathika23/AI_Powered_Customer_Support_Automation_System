"""Shared helpers for high-risk request detection and human approval."""

import re

HIGH_RISK_PATTERNS = [
    r"\brefund\b",
    r"\bmoney back\b",
    r"\breimbursement\b",
    r"\bcompensation\b",
    r"\bescalat(e|ion)\b",
    r"\bescalate to management\b",
    r"\bcancel(?: my)? subscription\b",
    r"\bcancellation\b",
    r"\bclose(?: my)? account\b",
    r"\baccount closure\b",
    r"\bdelete account\b",
]


def needs_human_approval(query: str) -> bool:
    """Return True when a request requires human supervisor review."""
    q = query.lower()
    return any(re.search(pattern, q) for pattern in HIGH_RISK_PATTERNS)
