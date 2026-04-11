import json
from pathlib import Path

import pytest

from secure_app.storage import NotesStore, safe_join


def test_safe_join_blocks_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        safe_join(tmp_path, "..", "evil.json")


def test_notes_store_add_and_list(tmp_path: Path) -> None:
    store = NotesStore(tmp_path)
    note = store.add_note("hello")
    notes = store.list_notes()
    assert len(notes) == 1
    assert notes[0].id == note.id
    assert notes[0].text == "hello"


def test_notes_store_rejects_bad_shape(tmp_path: Path) -> None:
    path = tmp_path / "notes.json"
    path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    store = NotesStore(tmp_path)
    with pytest.raises(ValueError):
        store.list_notes()
