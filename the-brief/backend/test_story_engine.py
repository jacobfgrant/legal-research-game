"""Tests for the story engine: YAML loading, conditions, consequences, scene resolution."""

import pytest

from models import GameState
from story_engine import StoryEngine


@pytest.fixture
def engine():
    e = StoryEngine()
    e.load()
    return e


@pytest.fixture
def fresh_state(engine):
    """A fresh game state at the start of chapter 1."""
    chapter = engine.chapters["chapter-01"]
    return GameState(
        save_id="test-save",
        current_chapter="chapter-01",
        current_scene=chapter.start_scene,
    )


class TestYAMLLoading:
    def test_manifest_loads(self, engine):
        assert engine.manifest is not None
        assert engine.manifest.title == "The Brief"
        assert len(engine.manifest.chapters) == 1

    def test_characters_load(self, engine):
        assert "margaret" in engine.characters
        assert engine.characters["margaret"].name == "Margaret Chen"
        assert "player" in engine.characters

    def test_chapter_loads(self, engine):
        chapter = engine.chapters["chapter-01"]
        assert chapter.title == "The Midnight Memo"
        assert chapter.start_scene == "late_night_office"

    def test_scenes_have_ids(self, engine):
        chapter = engine.chapters["chapter-01"]
        for scene_id, scene in chapter.scenes.items():
            assert scene.id == scene_id

    def test_research_items_have_ids(self, engine):
        chapter = engine.chapters["chapter-01"]
        for item_id, item in chapter.research_items.items():
            assert item.id == item_id

    def test_all_choice_targets_exist(self, engine):
        """Every choice target must reference an existing scene."""
        chapter = engine.chapters["chapter-01"]
        for scene_id, scene in chapter.scenes.items():
            if scene.choices:
                for choice in scene.choices:
                    assert choice.target in chapter.scenes, (
                        f"Scene '{scene_id}' choice '{choice.label}' "
                        f"targets non-existent scene '{choice.target}'"
                    )


class TestSceneResolution:
    def test_resolve_start_scene(self, engine, fresh_state):
        scene = engine.resolve_scene(fresh_state)
        assert scene is not None
        assert scene.id == "late_night_office"
        assert scene.act == "setup"
        assert "11:14 PM" in scene.text

    def test_start_scene_has_choices(self, engine, fresh_state):
        scene = engine.resolve_scene(fresh_state)
        assert scene.choices is not None
        assert len(scene.choices) == 2

    def test_dialogue_includes_character_info(self, engine, fresh_state):
        scene = engine.resolve_scene(fresh_state)
        assert scene.dialogue is not None
        assert "margaret" in scene.character_info
        assert scene.character_info["margaret"].name == "Margaret Chen"

    def test_terminal_scene_has_no_choices(self, engine, fresh_state):
        fresh_state.current_scene = "chapter_end_strong"
        scene = engine.resolve_scene(fresh_state)
        assert scene is not None
        assert scene.choices is None


class TestConditions:
    def test_condition_false_no_append(self, engine, fresh_state):
        """Without the flag, conditional text should not appear."""
        fresh_state.current_scene = "distinguish_baker"
        scene = engine.resolve_scene(fresh_state)
        assert "Having read Roth's motion" not in scene.text

    def test_condition_true_appends_text(self, engine, fresh_state):
        """With the flag set, conditional text should appear."""
        fresh_state.current_scene = "distinguish_baker"
        fresh_state.flags["read_opposition"] = True
        scene = engine.resolve_scene(fresh_state)
        assert "Having read Roth's motion" in scene.text

    def test_condition_dialogue_append(self, engine, fresh_state):
        """Condition with dialogue_append adds dialogue lines."""
        fresh_state.current_scene = "hearing_adequate"
        fresh_state.flags["used_persuasive"] = True
        scene = engine.resolve_scene(fresh_state)
        assert scene.dialogue is not None
        lines = [d.line for d in scene.dialogue]
        assert any("Martinez is Ninth Circuit" in line for line in lines)

    def test_condition_dialogue_not_appended_when_false(self, engine, fresh_state):
        fresh_state.current_scene = "hearing_adequate"
        # Don't set used_persuasive flag
        scene = engine.resolve_scene(fresh_state)
        assert scene.dialogue is not None
        lines = [d.line for d in scene.dialogue]
        assert not any("Martinez is Ninth Circuit" in line for line in lines)


class TestConsequences:
    def test_research_found(self, engine, fresh_state):
        """Choosing to research UCC should add it to research_found."""
        fresh_state.current_scene = "research_start"
        # Choice 0: "Start with the statute"
        state = engine.make_choice(fresh_state, 0)
        assert "ucc_section_2" in state.research_found

    def test_flag_set(self, engine, fresh_state):
        """Choosing to skip briefing should set the flag."""
        fresh_state.current_scene = "late_night_office"
        # Choice 1: "Head straight to the library"
        state = engine.make_choice(fresh_state, 1)
        assert state.flags.get("skipped_briefing") is True

    def test_relationship_increment(self, engine, fresh_state):
        """Asking Margaret for details should increment relationship."""
        fresh_state.current_scene = "late_night_office"
        # Choice 0: "Ask Margaret for more details"
        state = engine.make_choice(fresh_state, 0)
        assert state.relationships.get("margaret", 0) == 1

    def test_scene_entry_consequences(self, engine, fresh_state):
        """Scene-level consequences should apply on entry."""
        fresh_state.current_scene = "chen_case_discovery"
        # This scene has consequences: research_found: [chen_v_apex]
        # We need to enter it via a choice
        fresh_state.current_scene = "email_writing_cases"
        # Choice 0: "Dig deeper"
        state = engine.make_choice(fresh_state, 0)
        assert state.current_scene == "chen_case_discovery"
        assert "chen_v_apex" in state.research_found

    def test_relationship_decrement(self, engine, fresh_state):
        """Adequate memo should decrement margaret relationship."""
        fresh_state.current_scene = "adequate_memo"
        # adequate_memo has consequences: relationship.margaret: -1
        # These are scene-level, applied on entry
        # Let's reach it via email_writing_cases choice 1
        fresh_state.current_scene = "email_writing_cases"
        state = engine.make_choice(fresh_state, 1)
        assert state.current_scene == "adequate_memo"
        assert state.relationships.get("margaret", 0) == -1

    def test_choice_history_recorded(self, engine, fresh_state):
        state = engine.make_choice(fresh_state, 0)
        assert len(state.choice_history) == 1
        assert state.choice_history[0]["scene"] == "late_night_office"

    def test_no_duplicate_research(self, engine, fresh_state):
        """Adding the same research item twice shouldn't duplicate."""
        fresh_state.research_found = ["chen_v_apex"]
        fresh_state.current_scene = "email_writing_cases"
        # Choice 0 leads to chen_case_discovery which adds chen_v_apex
        state = engine.make_choice(fresh_state, 0)
        assert state.research_found.count("chen_v_apex") == 1


class TestResearchItems:
    def test_get_found_items(self, engine, fresh_state):
        fresh_state.research_found = ["ucc_section_2", "baker_v_telecom"]
        items = engine.get_research_items(fresh_state)
        assert len(items) == 2
        names = [i.name for i in items]
        assert "UCC Article 2, Section 2-201" in names
        assert "Baker v. Consolidated Telecom (2019)" in names

    def test_get_empty_research(self, engine, fresh_state):
        items = engine.get_research_items(fresh_state)
        assert items == []


class TestConditionEvaluation:
    def test_flag_truthy(self, engine, fresh_state):
        fresh_state.flags["test"] = True
        assert engine._evaluate_condition("flags.test", fresh_state)

    def test_flag_falsy(self, engine, fresh_state):
        assert not engine._evaluate_condition("flags.test", fresh_state)

    def test_relationship_comparison(self, engine, fresh_state):
        fresh_state.relationships["margaret"] = 3
        assert engine._evaluate_condition("relationship.margaret >= 2", fresh_state)
        assert not engine._evaluate_condition("relationship.margaret >= 5", fresh_state)

    def test_research_found_check(self, engine, fresh_state):
        fresh_state.research_found = ["baker_v_telecom"]
        assert engine._evaluate_condition("research_found.baker_v_telecom", fresh_state)
        assert not engine._evaluate_condition("research_found.chen_v_apex", fresh_state)


class TestFullPlaythrough:
    """Play through the strong path end to end."""

    def test_strong_path(self, engine, fresh_state):
        state = fresh_state

        # Ask Margaret for details
        state = engine.make_choice(state, 0)
        assert state.current_scene == "margaret_details"
        assert state.relationships["margaret"] == 1

        # Begin research
        state = engine.make_choice(state, 0)
        assert state.current_scene == "research_start"

        # Read opposing counsel's motion
        state = engine.make_choice(state, 2)
        assert state.current_scene == "read_motion"

        # Distinguish Baker (this choice sets read_opposition flag)
        state = engine.make_choice(state, 0)
        assert state.current_scene == "distinguish_baker"
        assert "baker_v_telecom" in state.research_found
        assert state.flags.get("read_opposition") is True

        # Search for automated vs manual signature cases
        state = engine.make_choice(state, 0)
        assert state.current_scene == "chen_case_discovery"
        assert "chen_v_apex" in state.research_found
        assert state.flags.get("found_distinction") is True

        # Build memo around Chen v. Apex
        state = engine.make_choice(state, 0)
        assert state.current_scene == "strong_memo"

        # Continue to hearing
        state = engine.make_choice(state, 0)
        assert state.current_scene == "hearing_strong"
        assert state.flags.get("chapter_01_strong_win") is True
        assert state.relationships["margaret"] >= 3

        # Continue to end
        state = engine.make_choice(state, 0)
        assert state.current_scene == "chapter_end_strong"
        assert state.flags.get("chapter_01_complete") is True
        assert state.flags.get("margaret_trust") is True

        # Terminal scene — no more choices
        scene = engine.resolve_scene(state)
        assert scene.choices is None
        assert scene.terminal is True
        assert scene.has_next_chapter is False  # no chapter 2 yet


class TestTerminalScenes:
    def test_terminal_scene_detected(self, engine, fresh_state):
        fresh_state.current_scene = "chapter_end_strong"
        assert engine.is_terminal_scene(fresh_state)

    def test_non_terminal_scene(self, engine, fresh_state):
        assert not engine.is_terminal_scene(fresh_state)

    def test_terminal_in_resolved_scene(self, engine, fresh_state):
        fresh_state.current_scene = "chapter_end_strong"
        scene = engine.resolve_scene(fresh_state)
        assert scene.terminal is True

    def test_non_terminal_in_resolved_scene(self, engine, fresh_state):
        scene = engine.resolve_scene(fresh_state)
        assert scene.terminal is False


class TestChapterTransition:
    def test_no_next_chapter_with_single_chapter(self, engine, fresh_state):
        fresh_state.flags["chapter_01_complete"] = True
        assert engine.get_next_chapter_id(fresh_state) is None

    def test_advance_returns_none_with_no_next(self, engine, fresh_state):
        assert engine.advance_chapter(fresh_state) is None
