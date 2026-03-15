"""Tests for API endpoints."""


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_scenarios(client):
    resp = client.get("/api/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["id"] == "non-compete"
    assert "scoring" not in data[0]


def test_get_scenario(client):
    resp = client.get("/api/scenarios/non-compete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "non-compete"
    assert "assignment" in data
    assert "argument_slots" in data
    assert "costs" in data
    # Scoring rubric must NOT be exposed
    assert "scoring" not in data


def test_get_scenario_not_found(client):
    resp = client.get("/api/scenarios/does-not-exist")
    assert resp.status_code == 404


def test_search_cases_with_results(client):
    resp = client.get("/api/scenarios/non-compete/search?q=non-compete")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["cases"]) > 0
    # Verify summaries don't leak full text
    first = data["cases"][0]
    assert "facts" not in first
    assert "holding" not in first
    assert "name" in first
    assert "citation" in first


def test_search_statutes_with_results(client):
    resp = client.get("/api/scenarios/non-compete/search?q=restrictive+covenant")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["statutes"]) > 0
    first = data["statutes"][0]
    assert "text" not in first
    assert "title" in first


def test_search_empty_query(client):
    resp = client.get("/api/scenarios/non-compete/search?q=")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cases"] == []
    assert data["statutes"] == []


def test_search_no_results(client):
    resp = client.get("/api/scenarios/non-compete/search?q=zzzzxyzzy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["cases"] == []


def test_get_case_detail(client):
    resp = client.get("/api/cases/non-compete/case_01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "case_01"
    assert "facts" in data
    assert "holding" in data
    assert "reasoning" in data
    assert "citations" in data
    # Scoring metadata must NOT be exposed
    assert "relevance_to_scenario" not in data
    assert "is_helpful" not in data


def test_get_case_not_found(client):
    resp = client.get("/api/cases/non-compete/case_99")
    assert resp.status_code == 404


def test_get_statute_detail(client):
    resp = client.get("/api/statutes/non-compete/statute_01")
    assert resp.status_code == 200
    data = resp.json()
    assert "text" in data
    assert "§ 542.330" in data["title"]


def test_create_session(client):
    resp = client.post("/api/sessions", json={"scenario_id": "non-compete"})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["scenario_id"] == "non-compete"


def test_create_session_bad_scenario(client):
    resp = client.post("/api/sessions", json={"scenario_id": "fake"})
    assert resp.status_code == 404


def test_submit_and_score(client):
    # Create session
    session = client.post(
        "/api/sessions", json={"scenario_id": "non-compete"}
    ).json()
    sid = session["session_id"]

    # Submit argument
    resp = client.post(f"/api/sessions/{sid}/submit", json={
        "slot_assignments": [
            {"slot_id": "foundation", "authority_id": "statute_01", "authority_type": "statute"},
            {"slot_id": "binding_precedent", "authority_id": "case_01", "authority_type": "case"},
        ],
        "hours_remaining": 6.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert data["score"]["total"] > 0
    assert data["score"]["grade"] in ("A", "B", "C", "D", "F")
    assert "ruling" in data

    # Retrieve score
    score_resp = client.get(f"/api/sessions/{sid}/score")
    assert score_resp.status_code == 200
    assert score_resp.json()["score"]["total"] == data["score"]["total"]


def test_submit_empty_argument(client):
    session = client.post(
        "/api/sessions", json={"scenario_id": "non-compete"}
    ).json()
    sid = session["session_id"]

    resp = client.post(f"/api/sessions/{sid}/submit", json={
        "slot_assignments": [],
        "hours_remaining": 12.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    # Only efficiency points for unused hours
    assert data["score"]["relevance"] == 0
    assert data["score"]["strength"] == 0
    assert data["score"]["efficiency"] > 0


def test_get_rebuttal(client):
    session = client.post(
        "/api/sessions", json={"scenario_id": "non-compete"}
    ).json()
    sid = session["session_id"]

    resp = client.get(f"/api/sessions/{sid}/rebuttal")
    assert resp.status_code == 200
    data = resp.json()
    assert "opposing_counsel" in data
    assert len(data["arguments"]) > 0
    # Counter hints must NOT be exposed
    for arg in data["arguments"]:
        assert "player_can_counter_with" not in arg
