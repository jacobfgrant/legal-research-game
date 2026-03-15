import type {
	NewGameResponse,
	ResolvedScene,
	ResearchItem,
	SaveSummary,
	ChapterSummary,
} from './types';

const BASE = '/api';
const TIMEOUT_MS = 10_000;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

	try {
		const resp = await fetch(`${BASE}${path}`, {
			headers: { 'Content-Type': 'application/json' },
			signal: controller.signal,
			...options,
		});
		if (!resp.ok) {
			let detail: string;
			try {
				detail = await resp.text();
			} catch {
				detail = `HTTP ${resp.status}`;
			}
			throw new Error(detail);
		}
		return resp.json();
	} catch (e) {
		if (e instanceof DOMException && e.name === 'AbortError') {
			throw new Error('Request timed out');
		}
		throw e;
	} finally {
		clearTimeout(timeout);
	}
}

export async function createGame(): Promise<NewGameResponse> {
	return request('/game/new', { method: 'POST' });
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
