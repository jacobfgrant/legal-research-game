"""Story engine: loads YAML content, resolves scenes, evaluates conditions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from models import (
    Chapter,
    Character,
    CharacterInfo,
    Condition,
    GameState,
    Manifest,
    ResolvedChoice,
    ResolvedScene,
    ResearchItem,
    Scene,
)

STORY_DIR = Path(__file__).parent / "story"


class StoryEngine:
    """Loads story content from YAML and resolves scenes against game state."""

    def __init__(self, story_dir: Path = STORY_DIR):
        self.story_dir = story_dir
        self.manifest: Manifest | None = None
        self.characters: dict[str, Character] = {}
        self.chapters: dict[str, Chapter] = {}

    def load(self) -> None:
        """Load all story content from YAML files."""
        self._load_manifest()
        self._load_characters()
        self._load_chapters()

    def _load_manifest(self) -> None:
        raw = self._read_yaml("manifest.yml")
        self.manifest = Manifest(**raw)

    def _load_characters(self) -> None:
        raw = self._read_yaml("characters.yml")
        for char_id, char_data in raw.get("characters", {}).items():
            char_data["id"] = char_id
            self.characters[char_id] = Character(**char_data)

    def _load_chapters(self) -> None:
        if not self.manifest:
            return
        for entry in self.manifest.chapters:
            raw = self._read_yaml(entry.file)
            # Inject scene IDs from dict keys
            for scene_id, scene_data in raw.get("scenes", {}).items():
                scene_data["id"] = scene_id
            # Inject research item IDs from dict keys
            for item_id, item_data in raw.get("research_items", {}).items():
                item_data["id"] = item_id
            self.chapters[entry.id] = Chapter(**raw)

    def _read_yaml(self, filename: str) -> dict:
        path = self.story_dir / filename
        with open(path) as f:
            return yaml.safe_load(f)

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        return self.chapters.get(chapter_id)

    def get_first_chapter_id(self) -> str | None:
        if self.manifest and self.manifest.chapters:
            return self.manifest.chapters[0].id
        return None

    def resolve_scene(self, state: GameState) -> ResolvedScene | None:
        """Resolve the current scene against game state.

        Evaluates conditions, filters choices, and returns a
        frontend-ready scene.
        """
        chapter = self.chapters.get(state.current_chapter)
        if not chapter:
            return None
        scene = chapter.scenes.get(state.current_scene)
        if not scene:
            return None

        text = scene.text
        dialogue = list(scene.dialogue) if scene.dialogue else None

        # Evaluate scene-level conditions
        if scene.conditions:
            for condition in scene.conditions:
                if self._evaluate_condition(condition.if_expr, state):
                    if condition.text_append:
                        text += "\n" + condition.text_append
                    if condition.dialogue_append:
                        if dialogue is None:
                            dialogue = []
                        dialogue.extend(condition.dialogue_append)

        # Filter and index choices
        resolved_choices: list[ResolvedChoice] | None = None
        if scene.choices:
            resolved_choices = []
            for i, choice in enumerate(scene.choices):
                if self._choice_available(choice, state):
                    resolved_choices.append(
                        ResolvedChoice(label=choice.label, index=i)
                    )
            if not resolved_choices:
                resolved_choices = None

        # Build character info for any characters in dialogue
        char_info: dict[str, CharacterInfo] = {}
        if dialogue:
            for line in dialogue:
                if line.character not in char_info:
                    char = self.characters.get(line.character)
                    if char:
                        char_info[line.character] = CharacterInfo(
                            name=char.name, title=char.title
                        )

        # Check terminal status and next chapter availability
        terminal = scene.terminal
        has_next = False
        if terminal:
            has_next = self.get_next_chapter_id(state) is not None

        return ResolvedScene(
            id=scene.id,
            act=scene.act,
            text=text.strip(),
            dialogue=dialogue,
            choices=resolved_choices,
            character_info=char_info,
            terminal=terminal,
            has_next_chapter=has_next,
            chapter_title=chapter.title,
        )

    def make_choice(self, state: GameState, choice_index: int) -> GameState:
        """Apply a choice: update state with consequences and advance scene."""
        chapter = self.chapters.get(state.current_chapter)
        if not chapter:
            return state
        scene = chapter.scenes.get(state.current_scene)
        if not scene or not scene.choices:
            return state
        if choice_index < 0 or choice_index >= len(scene.choices):
            return state

        choice = scene.choices[choice_index]

        # Record the choice
        state.choice_history.append({
            "chapter": state.current_chapter,
            "scene": state.current_scene,
            "choice": choice.label,
        })

        # Apply consequences
        if choice.consequences:
            self._apply_consequences(choice.consequences, state)

        # Advance to target scene
        state.current_scene = choice.target

        # Apply entry consequences on the new scene
        new_scene = chapter.scenes.get(choice.target)
        if new_scene and new_scene.consequences:
            self._apply_consequences(new_scene.consequences, state)

        return state

    def get_research_items(
        self, state: GameState
    ) -> list[ResearchItem]:
        """Return research items the player has found across all chapters."""
        items = []
        seen = set()
        for item_id in state.research_found:
            if item_id in seen:
                continue
            for chapter in self.chapters.values():
                if item_id in chapter.research_items:
                    items.append(chapter.research_items[item_id])
                    seen.add(item_id)
                    break
        return items

    def is_terminal_scene(self, state: GameState) -> bool:
        """Check if the current scene is a chapter-ending scene."""
        chapter = self.chapters.get(state.current_chapter)
        if not chapter:
            return False
        scene = chapter.scenes.get(state.current_scene)
        if not scene:
            return False
        return scene.terminal

    def get_next_chapter_id(self, state: GameState) -> str | None:
        """Find the next unlocked chapter after the current one."""
        if not self.manifest:
            return None
        current_found = False
        for entry in self.manifest.chapters:
            if entry.id == state.current_chapter:
                current_found = True
                continue
            if current_found:
                if entry.unlocked_by is None:
                    return entry.id
                if self._evaluate_condition(entry.unlocked_by, state):
                    return entry.id
        return None

    def advance_chapter(self, state: GameState) -> GameState | None:
        """Advance to the next chapter. Returns None if unavailable."""
        next_id = self.get_next_chapter_id(state)
        if not next_id:
            return None
        chapter = self.chapters.get(next_id)
        if not chapter:
            return None
        state.current_chapter = next_id
        state.current_scene = chapter.start_scene
        # Apply start scene entry consequences
        start_scene = chapter.scenes.get(chapter.start_scene)
        if start_scene and start_scene.consequences:
            self._apply_consequences(start_scene.consequences, state)
        return state

    def _evaluate_condition(self, expr: str, state: GameState) -> bool:
        """Evaluate a simple condition expression against game state.

        Supported forms:
            flags.some_flag             — truthy check
            relationship.name >= N      — numeric comparison
            research_found.item_id      — item in found list
        """
        expr = expr.strip()

        # Comparison operators
        match = re.match(r"^(.+?)\s*(>=|<=|>|<|==|!=)\s*(.+)$", expr)
        if match:
            left_str, op, right_str = match.groups()
            left_val = self._resolve_value(left_str.strip(), state)
            try:
                right_val = int(right_str.strip())
            except ValueError:
                right_val = right_str.strip()

            left_num = left_val if isinstance(left_val, int) else 0
            if isinstance(right_val, int):
                if op == ">=":
                    return left_num >= right_val
                if op == "<=":
                    return left_num <= right_val
                if op == ">":
                    return left_num > right_val
                if op == "<":
                    return left_num < right_val
                if op == "==":
                    return left_num == right_val
                if op == "!=":
                    return left_num != right_val
            return False

        # Dot-path truthy check
        return bool(self._resolve_value(expr, state))

    def _resolve_value(self, path: str, state: GameState) -> Any:
        """Resolve a dot-path to a value in game state."""
        parts = path.split(".", 1)
        domain = parts[0]

        if domain == "flags" and len(parts) == 2:
            return state.flags.get(parts[1])
        if domain == "relationship" and len(parts) == 2:
            return state.relationships.get(parts[1], 0)
        if domain == "career" and len(parts) == 2:
            return state.career.get(parts[1], 0)
        if domain == "research_found" and len(parts) == 2:
            return parts[1] in state.research_found

        return None

    def _choice_available(self, choice, state: GameState) -> bool:
        """Check if a choice's conditions are met."""
        if not choice.conditions:
            return True
        return all(
            self._evaluate_condition(c.if_expr, state)
            for c in choice.conditions
        )

    def _apply_consequences(
        self, consequences: dict[str, Any], state: GameState
    ) -> None:
        """Apply a consequences dict to game state."""
        for key, value in consequences.items():
            if key == "research_found":
                if isinstance(value, list):
                    for item_id in value:
                        if item_id not in state.research_found:
                            state.research_found.append(item_id)
                continue

            parts = key.split(".", 1)
            if len(parts) != 2:
                continue
            domain, field = parts

            if domain == "flags":
                state.flags[field] = value
            elif domain == "relationship":
                current = state.relationships.get(field, 0)
                state.relationships[field] = current + int(value)
            elif domain == "career":
                current = state.career.get(field, 0)
                state.career[field] = current + int(value)
