"""Persistent browser session metadata."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSION_DIR = Path.home() / ".cache" / "chrome-skill" / "sessions"
STALE_SECONDS = 24 * 60 * 60


def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"{session_id}.json"


def ensure_session_dir() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_stale_sessions() -> None:
    ensure_session_dir()
    now = time.time()
    for path in SESSION_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            path.unlink(missing_ok=True)
            continue
        created = data.get("created_at_epoch", 0)
        if now - created > STALE_SECONDS:
            close_session(data.get("session_id", path.stem), ignore_missing=True)


def create_session_record(
    *,
    pid: int,
    port: int,
    ws_url: str,
    user_data_dir: str,
    headed: bool,
    page_ws_url: str | None = None,
) -> dict[str, Any]:
    ensure_session_dir()
    cleanup_stale_sessions()
    session_id = secrets.token_hex(4)
    record = {
        "session_id": session_id,
        "pid": pid,
        "port": port,
        "ws_url": ws_url,
        "page_ws_url": page_ws_url,
        "user_data_dir": user_data_dir,
        "headed": headed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_at_epoch": time.time(),
    }
    _session_path(session_id).write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    return record


def load_session(session_id: str) -> dict[str, Any]:
    path = _session_path(session_id)
    if not path.exists():
        raise KeyError(f"Unknown session: {session_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def update_session(session_id: str, **updates: Any) -> dict[str, Any]:
    record = load_session(session_id)
    record.update(updates)
    _session_path(session_id).write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    return record


def list_sessions() -> list[dict[str, Any]]:
    ensure_session_dir()
    sessions: list[dict[str, Any]] = []
    for path in SESSION_DIR.glob("*.json"):
        try:
            sessions.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return sessions


def _terminate_pid(pid: int) -> None:
    if pid <= 0:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(20):
        try:
            os.kill(pid, 0)
            time.sleep(0.1)
        except ProcessLookupError:
            return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def close_session(session_id: str, *, ignore_missing: bool = False) -> dict[str, Any]:
    try:
        record = load_session(session_id)
    except KeyError:
        if ignore_missing:
            return {"session_id": session_id, "closed": False}
        raise

    _terminate_pid(int(record.get("pid", 0)))
    user_data_dir = record.get("user_data_dir")
    if user_data_dir and Path(user_data_dir).exists():
        shutil.rmtree(user_data_dir, ignore_errors=True)

    _session_path(session_id).unlink(missing_ok=True)
    return {"session_id": session_id, "closed": True}


def close_all_sessions() -> list[dict[str, Any]]:
    results = []
    for record in list_sessions():
        results.append(close_session(record["session_id"], ignore_missing=True))
    return results
