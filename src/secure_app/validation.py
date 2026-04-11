from __future__ import annotations

import re
import unicodedata

MAX_NOTE_LEN = 2000

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    # Normalize to reduce confusable / mixed-width edge cases.
    normalized = unicodedata.normalize("NFKC", text)

    # Remove embedded NULs (can cause truncation issues in some contexts).
    normalized = normalized.replace("\x00", "")
    return normalized


def validate_note_text(text: str) -> str:
    normalized = normalize_text(text).strip()
    if not normalized:
        raise ValueError("note text must not be empty")
    if len(normalized) > MAX_NOTE_LEN:
        raise ValueError(f"note text too long (max {MAX_NOTE_LEN})")

    # Avoid pathological whitespace-only notes.
    if not _WHITESPACE_RE.sub("", normalized):
        raise ValueError("note text must include non-whitespace characters")

    return normalized
