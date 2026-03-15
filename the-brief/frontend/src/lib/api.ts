import type {
	NewGameResponse,
	ResolvedScene,
	ResearchItem,
	SaveSummary,
	GameState,
	ChapterSummary,
} from './types';

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
	const resp = await fetch(`${BASE}${path}`, {
		headers: { 'Content-Type': 'application/json' },
		...options,
	});
	if (!resp.ok) {
		const detail = await resp.text();
		throw new Error(`API error ${resp.status}: ${detail}`);
	}
	return resp.json();
}

export async function createGame(): Promise<NewGameResponse> {
	return request('/game/new', { method: 'POST' });
}

export async function loadGame(saveId: string): Promise<GameState> {
	return request(`/game/${saveId}`);
}

export async function getScene(saveId: string): Promise<ResolvedScene> {
	return request(`/game/${saveId}/scene`);
}

export async function makeChoice(saveId: string, choiceIndex: number): Promise<ResolvedScene> {
	return request(`/game/${saveId}/choose`, {
		method: 'POST',
		body: JSON.stringify({ choice_index: choiceIndex }),
	});
}

export async function getResearch(saveId: string): Promise<ResearchItem[]> {
	return request(`/game/${saveId}/research`);
}

export async function listSaves(): Promise<SaveSummary[]> {
	return request('/saves');
}

export async function deleteSave(saveId: string): Promise<void> {
	await request(`/game/${saveId}`, { method: 'DELETE' });
}

export async function advanceChapter(saveId: string): Promise<ResolvedScene> {
	return request(`/game/${saveId}/advance`, { method: 'POST' });
}

export async function listChapters(): Promise<ChapterSummary[]> {
	return request('/chapters');
}
