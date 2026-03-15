"""Tests for the scoring algorithm."""

from scoring import score_argument


def test_perfect_argument(scenario):
    """Optimal authorities in correct slots should score near max."""
    result = score_argument(
        slot_assignments=[
            {"slot_id": "foundation", "authority_id": "statute_01", "authority_type": "statute"},
            {"slot_id": "binding_precedent", "authority_id": "case_01", "authority_type": "case"},
            {"slot_id": "persuasive_1", "authority_id": "case_04", "authority_type": "case"},
            {"slot_id": "persuasive_2", "authority_id": "case_09", "authority_type": "case"},
            {"slot_id": "counter", "authority_id": "case_07", "authority_type": "case"},
        ],
        hours_remaining=5.0,
        scenario=scenario,
    )
    assert result.grade == "A"
    assert result.total >= 85


def test_empty_argument(scenario):
    """No authorities should score only efficiency points."""
    result = score_argument([], hours_remaining=12.0, scenario=scenario)
    assert result.relevance == 0
    assert result.strength == 0
    assert result.completeness == 0
    assert result.efficiency == 15  # Full hours remaining
    assert result.total == 15
    assert result.grade == "F"


def test_zero_hours_remaining(scenario):
    """Spent all hours — efficiency should be 0."""
    result = score_argument(
        slot_assignments=[
            {"slot_id": "foundation", "authority_id": "statute_01", "authority_type": "statute"},
        ],
        hours_remaining=0.0,
        scenario=scenario,
    )
    assert result.efficiency == 0


def test_irrelevant_authority(scenario):
    """Authority not in the scoring rubric should contribute 0."""
    result = score_argument(
        slot_assignments=[
            {"slot_id": "foundation", "authority_id": "case_13", "authority_type": "case"},
        ],
        hours_remaining=10.0,
        scenario=scenario,
    )
    # case_13 (Wagner) isn't in authority_scores
    assert result.relevance == 0
    assert result.strength == 0


def test_wrong_slot_no_bonus(scenario):
    """Placing authority in wrong slot should lose the best-fit bonus."""
    # case_01's best fit is binding_precedent
    in_right_slot = score_argument(
        slot_assignments=[
            {"slot_id": "binding_precedent", "authority_id": "case_01", "authority_type": "case"},
        ],
        hours_remaining=6.0,
        scenario=scenario,
    )
    in_wrong_slot = score_argument(
        slot_assignments=[
            {"slot_id": "persuasive_1", "authority_id": "case_01", "authority_type": "case"},
        ],
        hours_remaining=6.0,
        scenario=scenario,
    )
    # Strength should be higher in the right slot (bonus of 2)
    assert in_right_slot.strength > in_wrong_slot.strength


def test_completeness_checklist(scenario):
    """Filling required slots with correct authorities earns completeness points."""
    with_foundation = score_argument(
        slot_assignments=[
            {"slot_id": "foundation", "authority_id": "statute_01", "authority_type": "statute"},
            {"slot_id": "binding_precedent", "authority_id": "case_01", "authority_type": "case"},
        ],
        hours_remaining=6.0,
        scenario=scenario,
    )
    without_foundation = score_argument(
        slot_assignments=[
            {"slot_id": "binding_precedent", "authority_id": "case_01", "authority_type": "case"},
        ],
        hours_remaining=6.0,
        scenario=scenario,
    )
    assert with_foundation.completeness > without_foundation.completeness


def test_efficiency_scaling(scenario):
    """More remaining hours should yield higher efficiency score."""
    high_efficiency = score_argument(
        slot_assignments=[],
        hours_remaining=10.0,
        scenario=scenario,
    )
    low_efficiency = score_argument(
        slot_assignments=[],
        hours_remaining=2.0,
        scenario=scenario,
    )
    assert high_efficiency.efficiency > low_efficiency.efficiency
