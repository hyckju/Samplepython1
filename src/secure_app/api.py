from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .demo import DummySensitiveDemo, generate_dummy_sensitive_demo
from .storage import Note, NotesStore


class AddNoteRequest(BaseModel):
    text: str = Field(..., description="Note text")


def create_app(*, data_dir: Path) -> FastAPI:
    app = FastAPI(title="secure-app", version="0.1.0")
    app.state.data_dir = data_dir

    @app.get("/notes", response_model=list[Note])
    def list_notes() -> list[Note]:
        try:
            store = NotesStore(Path(app.state.data_dir))
            return store.list_notes()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/notes", response_model=Note)
    def add_note(req: AddNoteRequest) -> Note:
        try:
            store = NotesStore(Path(app.state.data_dir))
            return store.add_note(req.text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/demo", response_model=DummySensitiveDemo)
    def demo() -> DummySensitiveDemo:
        return generate_dummy_sensitive_demo()

    return app


def main(argv: list[str] | None = None) -> int:
    """Entry-point for the packaged script.

    Runs an ASGI server via uvicorn.
    """

    import argparse

    parser = argparse.ArgumentParser(prog="secure-app")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Directory to store local JSON data (default: ./data)",
    )

    args = parser.parse_args(argv)

    # Local, file-based storage (no DB) in a user-provided directory.
    app = create_app(data_dir=Path(args.data_dir))

    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "uvicorn is required to run the API server; install requirements.txt"
        ) from exc

    uvicorn.run(app, host=args.host, port=args.port)
    return 0
