"""Case Crawler — FastAPI backend."""

import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import GameSession, SubmittedArgument, SearchLog  # noqa: F401

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

GAME_DATA_PATH = Path(
    os.environ.get("GAME_DATA_PATH", Path(__file__).parent / "game_data")
)

# In-memory stores populated at startup
_scenarios: dict[str, dict] = {}
_cases: dict[str, dict[str, dict]] = {}  # scenario_id -> {case_id -> case}
_statutes: dict[str, dict[str, dict]] = {}  # scenario_id -> {statute_id -> statute}
_rebuttals: dict[str, dict] = {}  # scenario_id -> rebuttal


def _load_game_data() -> None:
    """Load all JSON game data into memory."""
    for path in (GAME_DATA_PATH / "scenarios").glob("*.json"):
        scenario = json.loads(path.read_text())
        _scenarios[scenario["id"]] = scenario

    for path in (GAME_DATA_PATH / "cases").glob("*.json"):
        cases = json.loads(path.read_text())
        # Derive scenario id from filename: "non-compete-cases.json" -> "non-compete"
        scenario_id = path.stem.removesuffix("-cases")
        _cases[scenario_id] = {c["id"]: c for c in cases}

    for path in (GAME_DATA_PATH / "statutes").glob("*.json"):
        statutes = json.loads(path.read_text())
        scenario_id = path.stem.removesuffix("-statutes")
        _statutes[scenario_id] = {s["id"]: s for s in statutes}

    for path in (GAME_DATA_PATH / "rebuttals").glob("*.json"):
        rebuttal = json.loads(path.read_text())
        _rebuttals[rebuttal["scenario_id"]] = rebuttal


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def _search_cases(scenario_id: str, query: str) -> list[dict]:
    """Search cases by keyword. Returns summaries ranked by relevance."""
    cases = _cases.get(scenario_id, {})
    if not query.strip():
        return []

    tokens = query.lower().split()
    results = []

    for case in cases.values():
        # Build searchable text from tags, name, facts, holding
        searchable = " ".join([
            case["name"].lower(),
            " ".join(case["tags"]),
            case["facts"].lower(),
            case["holding"].lower(),
        ])
        # Count how many query tokens match
        matches = sum(1 for t in tokens if t in searchable)
        if matches > 0:
            results.append((matches, case))

    # Sort by match count descending, then by year descending
    results.sort(key=lambda x: (x[0], x[1]["year"]), reverse=True)

    # Return summaries only — no full text
    return [
        {
            "id": case["id"],
            "name": case["name"],
            "citation": case["citation"],
            "court": case["court"],
            "year": case["year"],
            "tags": case["tags"],
        }
        for _, case in results
    ]


def _search_statutes(scenario_id: str, query: str) -> list[dict]:
    """Search statutes by keyword. Returns summaries."""
    statutes = _statutes.get(scenario_id, {})
    if not query.strip():
        return []

    tokens = query.lower().split()
    results = []

    for statute in statutes.values():
        searchable = " ".join([
            statute["title"].lower(),
            " ".join(statute["tags"]),
            statute["text"].lower(),
        ])
        matches = sum(1 for t in tokens if t in searchable)
        if matches > 0:
            results.append((matches, statute))

    results.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "id": statute["id"],
            "title": statute["title"],
            "jurisdiction": statute["jurisdiction"],
            "tags": statute["tags"],
        }
        for _, statute in results
    ]


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load game data and create DB tables on startup."""
    _load_game_data()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Case Crawler API", lifespan=lifespan)


def get_db():
    """Yield a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pydantic models for request/response
# ---------------------------------------------------------------------------


class SessionCreate(BaseModel):
    scenario_id: str


class SessionResponse(BaseModel):
    session_id: str
    scenario_id: str


class SlotAssignment(BaseModel):
    slot_id: str
    authority_id: str
    authority_type: str  # "case" or "statute"


class ArgumentSubmission(BaseModel):
    slot_assignments: list[SlotAssignment]
    hours_remaining: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/scenarios")
def list_scenarios():
    """List available scenarios (no scoring data)."""
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "difficulty": s["difficulty"],
            "jurisdiction": s["jurisdiction"],
        }
        for s in _scenarios.values()
    ]


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Get scenario metadata for gameplay. Excludes the scoring rubric."""
    scenario = _scenarios.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Return everything except scoring data (the answer key)
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "difficulty": scenario["difficulty"],
        "jurisdiction": scenario["jurisdiction"],
        "court": scenario["court"],
        "client_side": scenario["client_side"],
        "assignment": scenario["assignment"],
        "billable_hours": scenario["billable_hours"],
        "costs": scenario["costs"],
        "argument_slots": scenario["argument_slots"],
        "search_hints": scenario.get("search_hints", []),
        "rulings": scenario["rulings"],
    }


@app.get("/api/scenarios/{scenario_id}/search")
def search_authorities(scenario_id: str, q: str = ""):
    """Search cases and statutes by keyword. Returns summaries only."""
    if scenario_id not in _scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "cases": _search_cases(scenario_id, q),
        "statutes": _search_statutes(scenario_id, q),
    }


@app.get("/api/cases/{scenario_id}/{case_id}")
def get_case(scenario_id: str, case_id: str):
    """Get full case detail (facts, holding, reasoning, citations)."""
    cases = _cases.get(scenario_id, {})
    case = cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Return everything except hidden scoring metadata
    return {
        "id": case["id"],
        "name": case["name"],
        "citation": case["citation"],
        "court": case["court"],
        "court_level": case["court_level"],
        "year": case["year"],
        "jurisdiction": case["jurisdiction"],
        "tags": case["tags"],
        "facts": case["facts"],
        "holding": case["holding"],
        "reasoning": case["reasoning"],
        "citations": case["citations"],
        "cited_by": case["cited_by"],
        "overruled": case["overruled"],
        "overruled_by": case["overruled_by"],
    }


@app.get("/api/statutes/{scenario_id}/{statute_id}")
def get_statute(scenario_id: str, statute_id: str):
    """Get full statute text."""
    statutes = _statutes.get(scenario_id, {})
    statute = statutes.get(statute_id)
    if not statute:
        raise HTTPException(status_code=404, detail="Statute not found")

    return {
        "id": statute["id"],
        "title": statute["title"],
        "jurisdiction": statute["jurisdiction"],
        "text": statute["text"],
        "effective_date": statute["effective_date"],
        "citations": statute["citations"],
        "cited_by": statute["cited_by"],
        "tags": statute["tags"],
    }


@app.post("/api/sessions", response_model=SessionResponse)
def create_session(body: SessionCreate, db: Session = Depends(get_db)):
    """Start a new game session."""
    if body.scenario_id not in _scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")

    session_id = str(uuid.uuid4())
    game_session = GameSession(id=session_id, scenario_id=body.scenario_id)
    db.add(game_session)
    db.commit()

    return SessionResponse(session_id=session_id, scenario_id=body.scenario_id)


@app.post("/api/sessions/{session_id}/submit")
def submit_argument(
    session_id: str,
    body: ArgumentSubmission,
    db: Session = Depends(get_db),
):
    """Submit a completed argument for scoring."""
    from scoring import score_argument

    game_session = db.query(GameSession).filter_by(id=session_id).first()
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")

    scenario = _scenarios.get(game_session.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Score the argument
    result = score_argument(
        slot_assignments=[sa.model_dump() for sa in body.slot_assignments],
        hours_remaining=body.hours_remaining,
        scenario=scenario,
    )

    # Persist results
    game_session.completed_at = datetime.now(timezone.utc)
    game_session.hours_remaining = body.hours_remaining
    game_session.score_total = result.total
    game_session.score_relevance = result.relevance
    game_session.score_strength = result.strength
    game_session.score_completeness = result.completeness
    game_session.score_efficiency = result.efficiency

    for sa in body.slot_assignments:
        db.add(SubmittedArgument(
            session_id=session_id,
            slot_id=sa.slot_id,
            authority_id=sa.authority_id,
            authority_type=sa.authority_type,
        ))

    db.commit()

    # Build ruling text from grade
    ruling_data = scenario.get("rulings", {}).get(result.grade, {})

    return {
        "score": {
            "relevance": result.relevance,
            "strength": result.strength,
            "completeness": result.completeness,
            "efficiency": result.efficiency,
            "total": result.total,
            "grade": result.grade,
        },
        "details": result.details,
        "ruling": ruling_data,
    }


@app.get("/api/sessions/{session_id}/rebuttal")
def get_rebuttal(session_id: str, db: Session = Depends(get_db)):
    """Get opposition rebuttal for a completed session."""
    game_session = db.query(GameSession).filter_by(id=session_id).first()
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")

    rebuttal = _rebuttals.get(game_session.scenario_id)
    if not rebuttal:
        raise HTTPException(status_code=404, detail="Rebuttal not found")

    # Don't leak the player_can_counter_with hints
    return {
        "opposing_counsel": rebuttal["opposing_counsel"],
        "intro": rebuttal["intro"],
        "arguments": [
            {
                "id": arg["id"],
                "type": arg["type"],
                "authority_id": arg["authority_id"],
                "summary": arg["summary"],
                "strength": arg["strength"],
            }
            for arg in rebuttal["arguments"]
        ],
        "closing": rebuttal["closing"],
    }


@app.get("/api/sessions/{session_id}/score")
def get_score(session_id: str, db: Session = Depends(get_db)):
    """Get score for a completed session."""
    game_session = db.query(GameSession).filter_by(id=session_id).first()
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if game_session.score_total is None:
        raise HTTPException(status_code=400, detail="Session not yet scored")

    # Determine grade from total
    total = game_session.score_total
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

    scenario = _scenarios.get(game_session.scenario_id, {})
    ruling_data = scenario.get("rulings", {}).get(grade, {})

    return {
        "score": {
            "relevance": game_session.score_relevance,
            "strength": game_session.score_strength,
            "completeness": game_session.score_completeness,
            "efficiency": game_session.score_efficiency,
            "total": game_session.score_total,
            "grade": grade,
        },
        "ruling": ruling_data,
        "hours_remaining": game_session.hours_remaining,
    }
