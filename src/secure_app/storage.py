from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validation import validate_note_text


def safe_join(base_dir: Path, *parts: str) -> Path:
    base = base_dir.resolve(strict=False)
    candidate = base.joinpath(*parts).resolve(strict=False)

    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("path traversal detected") from exc

    return candidate


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_path, path)


@dataclass(frozen=True)
class Note:
    id: str
    text: str
    created_at: str


class NotesStore:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._path = safe_join(data_dir, "notes.json")

    def list_notes(self) -> list[Note]:
        if not self._path.exists():
            return []

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("notes.json must be a list")

        notes: list[Note] = []
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("note must be an object")
            note_id = item.get("id")
            text = item.get("text")
            created_at = item.get("created_at")
            if not isinstance(note_id, str) or not isinstance(text, str) or not isinstance(created_at, str):
                raise ValueError("invalid note shape")
            notes.append(Note(id=note_id, text=text, created_at=created_at))

        return notes

    def add_note(self, text: str) -> Note:
        normalized = validate_note_text(text)

        now = datetime.now(timezone.utc).isoformat()
        note = Note(
            id=os.urandom(8).hex(),
            text=normalized,
            created_at=now,
        )

        notes = self.list_notes()
        notes.append(note)
        _atomic_write_json(self._path, [asdict(n) for n in notes])
        return note
