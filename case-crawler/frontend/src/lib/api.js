/**
 * Fetch wrapper for the Case Crawler API.
 * In dev, Vite proxies /api to localhost:8000.
 * In production, Caddy routes /api to the backend.
 */

async function request(path, options = {}) {
	const resp = await fetch(path, {
		headers: { 'Content-Type': 'application/json', ...options.headers },
		...options,
	});
	if (!resp.ok) {
		const detail = await resp.json().catch(() => ({}));
		throw new Error(detail.detail || `API error: ${resp.status}`);
	}
	return resp.json();
}

export function listScenarios() {
	return request('/api/scenarios');
}

export function getScenario(id) {
	return request(`/api/scenarios/${id}`);
}

export function searchAuthorities(scenarioId, query) {
	return request(`/api/scenarios/${scenarioId}/search?q=${encodeURIComponent(query)}`);
}

export function getCase(scenarioId, caseId) {
	return request(`/api/cases/${scenarioId}/${caseId}`);
}

export function getStatute(scenarioId, statuteId) {
	return request(`/api/statutes/${scenarioId}/${statuteId}`);
}

export function createSession(scenarioId) {
	return request('/api/sessions', {
		method: 'POST',
		body: JSON.stringify({ scenario_id: scenarioId }),
	});
}

export function submitArgument(sessionId, slotAssignments, hoursRemaining) {
	return request(`/api/sessions/${sessionId}/submit`, {
		method: 'POST',
		body: JSON.stringify({
			slot_assignments: slotAssignments,
			hours_remaining: hoursRemaining,
		}),
	});
}

export function getRebuttal(sessionId) {
	return request(`/api/sessions/${sessionId}/rebuttal`);
}

export function getScore(sessionId) {
	return request(`/api/sessions/${sessionId}/score`);
}
