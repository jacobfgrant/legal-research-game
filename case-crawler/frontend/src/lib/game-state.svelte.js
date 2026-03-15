/**
 * Central game state using Svelte 5 runes.
 * All pages read from and write to this shared module.
 */

/** @type {'select' | 'briefing' | 'research' | 'argument' | 'rebuttal' | 'score'} */
let gamePhase = $state('select');

let scenario = $state(null);
let sessionId = $state(null);
let billableHours = $state(0);

/** @type {Array<{id: string, type: 'case'|'statute', name: string, citation?: string, title?: string, court?: string, year?: number}>} */
let collectedAuthorities = $state([]);

/** @type {Object<string, {authority_id: string, authority_type: string}>} */
let slotAssignments = $state({});

/** @type {Array<{query: string, resultCount: number}>} */
let searchHistory = $state([]);

let currentDetail = $state(null);
let scoreResult = $state(null);
let rebuttalData = $state(null);

// --- Derived state ---

let hoursSpent = $derived(scenario ? scenario.billable_hours - billableHours : 0);
let canSearch = $derived(billableHours >= (scenario?.costs?.search ?? Infinity));
let canReadCase = $derived(billableHours >= (scenario?.costs?.read_case ?? Infinity));
let canReadStatute = $derived(billableHours >= (scenario?.costs?.read_statute ?? Infinity));
let canFollowCitation = $derived(billableHours >= (scenario?.costs?.follow_citation ?? Infinity));
let hoursExpired = $derived(scenario !== null && billableHours <= 0);

let filledSlots = $derived(Object.keys(slotAssignments).length);
let requiredSlotsFilled = $derived(
	scenario?.argument_slots
		?.filter(s => s.required)
		.every(s => slotAssignments[s.slot_id]) ?? false
);

// --- Actions ---

export function startScenario(scenarioData, newSessionId) {
	scenario = scenarioData;
	sessionId = newSessionId;
	billableHours = scenarioData.billable_hours;
	collectedAuthorities = [];
	slotAssignments = {};
	searchHistory = [];
	currentDetail = null;
	scoreResult = null;
	rebuttalData = null;
	gamePhase = 'briefing';
}

export function beginResearch() {
	gamePhase = 'research';
}

export function goToArgument() {
	gamePhase = 'argument';
}

export function goToResearch() {
	gamePhase = 'research';
}

export function goToRebuttal(data) {
	rebuttalData = data;
	gamePhase = 'rebuttal';
}

export function setScoreResult(result) {
	scoreResult = result;
}

export function goToScore() {
	gamePhase = 'score';
}

export function spendHours(action) {
	if (!scenario) return false;
	const cost = scenario.costs[action] ?? 0;
	if (billableHours < cost) return false;
	billableHours -= cost;
	return true;
}

export function collectAuthority(authority) {
	if (collectedAuthorities.some(a => a.id === authority.id)) return;
	collectedAuthorities = [...collectedAuthorities, authority];
}

export function assignToSlot(slotId, authorityId, authorityType) {
	slotAssignments = { ...slotAssignments, [slotId]: { authority_id: authorityId, authority_type: authorityType } };
}

export function removeFromSlot(slotId) {
	const { [slotId]: _, ...rest } = slotAssignments;
	slotAssignments = rest;
}

export function setCurrentDetail(detail) {
	currentDetail = detail;
}

export function logSearch(query, resultCount) {
	searchHistory = [...searchHistory, { query, resultCount }];
}

export function resetGame() {
	scenario = null;
	sessionId = null;
	billableHours = 0;
	collectedAuthorities = [];
	slotAssignments = {};
	searchHistory = [];
	currentDetail = null;
	scoreResult = null;
	rebuttalData = null;
	gamePhase = 'select';
}

// --- Getters (reactive reads) ---

export function getState() {
	return {
		gamePhase,
		scenario,
		sessionId,
		billableHours,
		collectedAuthorities,
		slotAssignments,
		searchHistory,
		currentDetail,
		scoreResult,
		rebuttalData,
		hoursSpent,
		canSearch,
		canReadCase,
		canReadStatute,
		canFollowCitation,
		hoursExpired,
		filledSlots,
		requiredSlotsFilled,
	};
}
