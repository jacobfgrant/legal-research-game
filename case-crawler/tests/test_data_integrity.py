"""Tests that validate game data files for internal consistency."""

import json
from pathlib import Path

import pytest

DATA_PATH = Path(__file__).parent.parent / "backend" / "game_data"


@pytest.fixture(scope="module")
def cases():
    path = DATA_PATH / "cases" / "non-compete-cases.json"
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def statutes():
    path = DATA_PATH / "statutes" / "non-compete-statutes.json"
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def scenario_data():
    path = DATA_PATH / "scenarios" / "non-compete.json"
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def rebuttal():
    path = DATA_PATH / "rebuttals" / "non-compete-rebuttal.json"
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def all_ids(cases, statutes):
    """Set of all case and statute IDs."""
    return {c["id"] for c in cases} | {s["id"] for s in statutes}


def test_json_files_parse():
    """Every JSON file in game_data should parse without error."""
    for path in DATA_PATH.rglob("*.json"):
        data = json.loads(path.read_text())
        assert data is not None, f"Failed to parse {path}"


def test_case_citations_resolve(cases, all_ids):
    """Every citation in every case should reference an existing ID."""
    for case in cases:
        for cited_id in case["citations"]:
            assert cited_id in all_ids, (
                f'{case["id"]} cites {cited_id} which does not exist'
            )


def test_case_cited_by_resolve(cases, all_ids):
    """Every cited_by reference should exist."""
    for case in cases:
        for cited_by_id in case["cited_by"]:
            assert cited_by_id in all_ids, (
                f'{case["id"]} cited_by {cited_by_id} which does not exist'
            )


def test_statute_cited_by_resolve(statutes, all_ids):
    """Every cited_by in statutes should reference an existing case."""
    for statute in statutes:
        for cited_by_id in statute["cited_by"]:
            assert cited_by_id in all_ids, (
                f'{statute["id"]} cited_by {cited_by_id} which does not exist'
            )


def test_scoring_authority_ids_exist(scenario_data, all_ids):
    """Every ID in authority_scores should exist in the case/statute data."""
    for auth_id in scenario_data["scoring"]["authority_scores"]:
        assert auth_id in all_ids, (
            f"Scoring references {auth_id} which does not exist in game data"
        )


def test_completeness_checklist_ids_exist(scenario_data, all_ids):
    """Every authority ID in completeness conditions should exist."""
    for check in scenario_data["scoring"]["completeness_checklist"]:
        condition = check["condition"]
        if "authority_ids" in condition:
            for auth_id in condition["authority_ids"]:
                assert auth_id in all_ids, (
                    f'Checklist "{check["id"]}" references {auth_id} '
                    f"which does not exist"
                )


def test_rebuttal_authority_ids_exist(rebuttal, all_ids):
    """Every authority referenced in rebuttal should exist."""
    for arg in rebuttal["arguments"]:
        assert arg["authority_id"] in all_ids, (
            f'Rebuttal references {arg["authority_id"]} which does not exist'
        )
        if "player_can_counter_with" in arg:
            for counter_id in arg["player_can_counter_with"]:
                assert counter_id in all_ids, (
                    f'Rebuttal counter references {counter_id} which does not exist'
                )


def test_no_duplicate_case_ids(cases):
    """All case IDs should be unique."""
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids)), "Duplicate case IDs found"


def test_no_duplicate_statute_ids(statutes):
    """All statute IDs should be unique."""
    ids = [s["id"] for s in statutes]
    assert len(ids) == len(set(ids)), "Duplicate statute IDs found"


def test_citation_bidirectionality(cases, all_ids):
    """If A cites B, then B's cited_by should include A (for cases)."""
    case_map = {c["id"]: c for c in cases}
    for case in cases:
        for cited_id in case["citations"]:
            if cited_id in case_map:
                cited_case = case_map[cited_id]
                assert case["id"] in cited_case["cited_by"], (
                    f'{case["id"]} cites {cited_id} but {cited_id} '
                    f'does not list {case["id"]} in cited_by'
                )
