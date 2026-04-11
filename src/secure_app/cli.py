from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .demo import generate_dummy_sensitive_demo
from .storage import NotesStore


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="secure-app")
    p.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store local JSON data (default: ./data)",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    add_p = sub.add_parser("add", help="Add a note")
    add_p.add_argument("--text", help="Note text; if omitted, read from stdin")

    sub.add_parser("list", help="List notes")

    sub.add_parser(
        "demo",
        help="Print a safe dummy sensitive-data example (generated at runtime, masked; no hardcoded secrets)",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.cmd == "add":
        store = NotesStore(Path(args.data_dir))
        text = args.text
        if text is None:
            text = sys.stdin.read()
        note = store.add_note(text)
        print(note.id)
        return 0

    if args.cmd == "list":
        store = NotesStore(Path(args.data_dir))
        for n in store.list_notes():
            print(f"{n.created_at} {n.id} {n.text}")
        return 0

    if args.cmd == "demo":
        demo = generate_dummy_sensitive_demo()
        # Printed output is already masked + password is only shown as a strong hash.
        sys.stdout.write(demo.to_json())
        return 0

    raise RuntimeError("unreachable")
