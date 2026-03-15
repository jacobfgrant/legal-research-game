"""SQLite persistence for game saves."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models import GameState, SaveSummary

DEFAULT_DB_PATH = Path("/app/data/the_brief.db")


class Database:
    """Simple SQLite wrapper for game save persistence."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_table()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(self.db_path))

    def _ensure_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS game_saves (
                    save_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def save_game(self, state: GameState) -> None:
        """Insert or update a game save."""
        now = datetime.now(timezone.utc).isoformat()
        state.updated_at = now
        if not state.created_at:
            state.created_at = now

        state_json = state.model_dump_json()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO game_saves (save_id, state_json, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(save_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = excluded.updated_at
                """,
                (state.save_id, state_json, state.created_at, now),
            )

    def load_game(self, save_id: str) -> GameState | None:
        """Load a game save by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state_json FROM game_saves WHERE save_id = ?",
                (save_id,),
            ).fetchone()
        if not row:
            return None
        return GameState(**json.loads(row[0]))

    def list_saves(self) -> list[SaveSummary]:
        """List all saves with summary info."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT state_json, updated_at FROM game_saves ORDER BY updated_at DESC"
            ).fetchall()

        summaries = []
        for state_json, updated_at in rows:
            data = json.loads(state_json)
            summaries.append(SaveSummary(
                save_id=data["save_id"],
                current_chapter=data["current_chapter"],
                current_scene=data["current_scene"],
                updated_at=updated_at,
            ))
        return summaries

    def delete_save(self, save_id: str) -> bool:
        """Delete a save. Returns True if a row was deleted."""
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM game_saves WHERE save_id = ?",
                (save_id,),
            )
        return cursor.rowcount > 0
