"""The Brief — FastAPI application."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException

from database import Database
from models import (
    ChapterSummary,
    Character,
    ChooseRequest,
    GameState,
    NewGameResponse,
    ResolvedScene,
    ResearchItem,
    SaveSummary,
)
from story_engine import StoryEngine

app = FastAPI(title="The Brief", version="0.1.0")

# Initialize story engine and database
engine = StoryEngine()
engine.load()

db_path = Path(os.environ.get("DB_PATH", "/app/data/the_brief.db"))
db = Database(db_path)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/chapters")
async def list_chapters() -> list[ChapterSummary]:
    """List available chapters."""
    if not engine.manifest:
        return []
    return [
        ChapterSummary(id=e.id, title=e.title, description=e.description)
        for e in engine.manifest.chapters
    ]


@app.get("/api/characters")
async def list_characters() -> dict[str, Character]:
    """Get all character definitions."""
    return engine.characters


@app.post("/api/game/new")
async def new_game() -> NewGameResponse:
    """Start a new game."""
    chapter_id = engine.get_first_chapter_id()
    if not chapter_id:
        raise HTTPException(status_code=500, detail="No chapters available")

    chapter = engine.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=500, detail="Chapter not found")

    state = GameState(
        save_id=str(uuid.uuid4()),
        current_chapter=chapter_id,
        current_scene=chapter.start_scene,
    )

    # Apply entry consequences on the start scene
    start_scene = chapter.scenes.get(chapter.start_scene)
    if start_scene and start_scene.consequences:
        engine._apply_consequences(start_scene.consequences, state)

    db.save_game(state)

    scene = engine.resolve_scene(state)
    if not scene:
        raise HTTPException(status_code=500, detail="Could not resolve start scene")

    return NewGameResponse(save_id=state.save_id, scene=scene)


@app.get("/api/game/{save_id}")
async def get_game(save_id: str) -> GameState:
    """Load game state."""
    state = db.load_game(save_id)
    if not state:
        raise HTTPException(status_code=404, detail="Save not found")
    return state


@app.get("/api/game/{save_id}/scene")
async def get_scene(save_id: str) -> ResolvedScene:
    """Get the current resolved scene."""
    state = db.load_game(save_id)
    if not state:
        raise HTTPException(status_code=404, detail="Save not found")

    scene = engine.resolve_scene(state)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene


@app.post("/api/game/{save_id}/choose")
async def make_choice(save_id: str, request: ChooseRequest) -> ResolvedScene:
    """Make a choice in the current scene."""
    state = db.load_game(save_id)
    if not state:
        raise HTTPException(status_code=404, detail="Save not found")

    # Validate the choice exists
    chapter = engine.get_chapter(state.current_chapter)
    if not chapter:
        raise HTTPException(status_code=500, detail="Chapter not found")
    scene = chapter.scenes.get(state.current_scene)
    if not scene or not scene.choices:
        raise HTTPException(status_code=400, detail="No choices available")
    if request.choice_index < 0 or request.choice_index >= len(scene.choices):
        raise HTTPException(status_code=400, detail="Invalid choice index")

    # Apply the choice
    state = engine.make_choice(state, request.choice_index)
    db.save_game(state)

    # Return the new scene
    new_scene = engine.resolve_scene(state)
    if not new_scene:
        raise HTTPException(status_code=500, detail="Could not resolve next scene")
    return new_scene


@app.get("/api/game/{save_id}/research")
async def get_research(save_id: str) -> list[ResearchItem]:
    """Get research items the player has found."""
    state = db.load_game(save_id)
    if not state:
        raise HTTPException(status_code=404, detail="Save not found")
    return engine.get_research_items(state)


@app.get("/api/saves")
async def list_saves() -> list[SaveSummary]:
    """List all game saves."""
    return db.list_saves()


@app.delete("/api/game/{save_id}")
async def delete_game(save_id: str):
    """Delete a game save."""
    if not db.delete_save(save_id):
        raise HTTPException(status_code=404, detail="Save not found")
    return {"status": "deleted"}
