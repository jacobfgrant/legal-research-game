"""Pydantic models for story content and game state."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# --- Story content models (loaded from YAML) ---


class DialogueLine(BaseModel):
    character: str
    line: str


class Condition(BaseModel):
    if_expr: str = Field(alias="if")
    text_append: str | None = None
    dialogue_append: list[DialogueLine] | None = None


class Choice(BaseModel):
    label: str
    target: str
    conditions: list[Condition] | None = None
    consequences: dict[str, Any] | None = None


class Scene(BaseModel):
    id: str = ""
    act: str
    text: str
    dialogue: list[DialogueLine] | None = None
    conditions: list[Condition] | None = None
    choices: list[Choice] | None = None
    consequences: dict[str, Any] | None = None
    terminal: bool = False


class ResearchItem(BaseModel):
    id: str = ""
    name: str
    description: str
    type: str
    jurisdiction: str | None = None


class Character(BaseModel):
    id: str = ""
    name: str
    title: str
    description: str


class Chapter(BaseModel):
    id: str
    title: str
    description: str
    characters: list[str]
    research_items: dict[str, ResearchItem]
    scenes: dict[str, Scene]
    start_scene: str


class ChapterSummary(BaseModel):
    id: str
    title: str
    description: str


class ManifestEntry(BaseModel):
    id: str
    file: str
    title: str
    description: str
    unlocked_by: str | None = None


class Manifest(BaseModel):
    title: str
    version: str
    chapters: list[ManifestEntry]


# --- Game state (persisted to SQLite) ---


class GameState(BaseModel):
    save_id: str
    current_chapter: str
    current_scene: str
    research_found: list[str] = Field(default_factory=list)
    flags: dict[str, Any] = Field(default_factory=dict)
    relationships: dict[str, int] = Field(default_factory=dict)
    career: dict[str, int] = Field(default_factory=dict)
    choice_history: list[dict[str, str]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


# --- API response models ---


class CharacterInfo(BaseModel):
    name: str
    title: str


class ResolvedScene(BaseModel):
    """Scene after condition evaluation — what the frontend receives."""

    id: str
    act: str
    text: str
    dialogue: list[DialogueLine] | None = None
    choices: list[ResolvedChoice] | None = None
    character_info: dict[str, CharacterInfo] = Field(default_factory=dict)
    terminal: bool = False
    has_next_chapter: bool = False
    chapter_title: str = ""


class ResolvedChoice(BaseModel):
    """Choice stripped of internals — frontend only needs label + index."""

    label: str
    index: int


# Rebuild ResolvedScene now that ResolvedChoice is defined
ResolvedScene.model_rebuild()


class NewGameResponse(BaseModel):
    save_id: str
    scene: ResolvedScene


class SaveSummary(BaseModel):
    save_id: str
    current_chapter: str
    current_scene: str
    chapter_title: str = ""
    updated_at: str


class ChooseRequest(BaseModel):
    choice_index: int
