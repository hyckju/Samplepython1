import pytest

from secure_app.validation import MAX_NOTE_LEN, validate_note_text


def test_validate_note_text_basic() -> None:
    assert validate_note_text(" hello ") == "hello"


def test_validate_note_text_rejects_empty() -> None:
    with pytest.raises(ValueError):
        validate_note_text("   \n\t")


def test_validate_note_text_len_limit() -> None:
    with pytest.raises(ValueError):
        validate_note_text("a" * (MAX_NOTE_LEN + 1))
