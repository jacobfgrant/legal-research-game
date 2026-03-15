"""Server-side scoring algorithm for argument evaluation."""

from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    """Full score breakdown for a submitted argument."""

    relevance: int
    strength: int
    completeness: int
    efficiency: int
    total: int
    grade: str
    details: dict


def evaluate_condition(
    condition: dict,
    slot_map: dict[str, str],
    submitted_ids: set[str],
) -> bool:
    """Evaluate a single completeness checklist condition."""
    ctype = condition["type"]

    if ctype == "slot_contains_any":
        assigned = slot_map.get(condition["slot_id"])
        return assigned in condition["authority_ids"]

    if ctype == "any_submitted":
        return bool(submitted_ids & set(condition["authority_ids"]))

    return False


def score_argument(
    slot_assignments: list[dict],
    hours_remaining: float,
    scenario: dict,
) -> ScoreBreakdown:
    """Score a submitted argument against the scenario's rubric."""
    scoring = scenario["scoring"]
    authority_scores = scoring["authority_scores"]
    checklist = scoring["completeness_checklist"]

    # Build lookup structures
    slot_map = {sa["slot_id"]: sa["authority_id"] for sa in slot_assignments}
    submitted_ids = {sa["authority_id"] for sa in slot_assignments}

    # --- Relevance (max 30) ---
    relevance = 0
    relevance_details = []
    for sa in slot_assignments:
        auth = authority_scores.get(sa["authority_id"], {})
        points = auth.get("relevance", 0)
        relevance += points
        relevance_details.append({
            "authority_id": sa["authority_id"],
            "slot_id": sa["slot_id"],
            "points": points,
            "notes": auth.get("notes", "Not in scoring rubric"),
        })
    relevance = min(relevance, scoring["categories"]["relevance"]["max"])

    # --- Strength (max 30) ---
    strength = 0
    strength_details = []
    for sa in slot_assignments:
        auth = authority_scores.get(sa["authority_id"], {})
        base = auth.get("strength", 0)
        bonus = 2 if auth.get("slot_best_fit") == sa["slot_id"] else 0
        points = base + bonus
        strength += points
        strength_details.append({
            "authority_id": sa["authority_id"],
            "slot_id": sa["slot_id"],
            "base": base,
            "slot_bonus": bonus,
            "points": points,
        })
    strength = min(strength, scoring["categories"]["strength"]["max"])

    # --- Completeness (max 25) ---
    completeness = 0
    completeness_details = []
    for check in checklist:
        met = evaluate_condition(check["condition"], slot_map, submitted_ids)
        points = check["points"] if met else 0
        completeness += points
        completeness_details.append({
            "check_id": check["id"],
            "description": check["description"],
            "met": met,
            "points": points,
        })
    completeness = min(completeness, scoring["categories"]["completeness"]["max"])

    # --- Efficiency (max 15) ---
    total_budget = scenario["billable_hours"]
    fraction = max(hours_remaining, 0) / total_budget if total_budget > 0 else 0
    efficiency = round(fraction * scoring["categories"]["efficiency"]["max"])
    efficiency = min(efficiency, scoring["categories"]["efficiency"]["max"])

    # --- Total and grade ---
    total = relevance + strength + completeness + efficiency
    total = min(total, scoring["max_score"])

    if total >= 90:
        grade = "A"
    elif total >= 75:
        grade = "B"
    elif total >= 60:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"

    return ScoreBreakdown(
        relevance=relevance,
        strength=strength,
        completeness=completeness,
        efficiency=efficiency,
        total=total,
        grade=grade,
        details={
            "relevance": relevance_details,
            "strength": strength_details,
            "completeness": completeness_details,
            "efficiency": {
                "hours_remaining": hours_remaining,
                "total_budget": total_budget,
                "fraction": round(fraction, 3),
            },
        },
    )
