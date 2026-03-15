import { goto } from '$app/navigation';
import * as api from './api';
import type { ResolvedScene, ResearchItem } from './types';

export const game = $state({
	saveId: null as string | null,
	scene: null as ResolvedScene | null,
	research: [] as ResearchItem[],
	loading: false,
	error: null as string | null,
	showResearch: false,
});

export const sceneState = $state({
	/** Which dialogue line we're currently showing (null = showing narrative text) */
	dialogueIndex: null as number | null,
	/** Whether all text has been revealed (for typewriter effect) */
	textRevealed: false,
	/** Whether choices are visible */
	showChoices: false,
});

function resetSceneState() {
	sceneState.dialogueIndex = null;
	sceneState.textRevealed = false;
	sceneState.showChoices = false;
}

function onSceneLoaded() {
	resetSceneState();
	// If scene has dialogue, start at narrative text (dialogueIndex = null)
	// Player clicks to advance through dialogue, then sees choices
	// If no dialogue, reveal choices after text
	if (!game.scene?.dialogue?.length) {
		sceneState.showChoices = true;
	}
}

export async function startNewGame() {
	game.loading = true;
	game.error = null;
	try {
		const resp = await api.createGame();
		game.saveId = resp.save_id;
		game.scene = resp.scene;
		game.research = [];
		onSceneLoaded();
		goto(`/game/${resp.save_id}`);
	} catch (e) {
		game.error = e instanceof Error ? e.message : 'Failed to start game';
	} finally {
		game.loading = false;
	}
}

export async function loadExistingGame(saveId: string) {
	game.loading = true;
	game.error = null;
	try {
		game.saveId = saveId;
		const [scene, research] = await Promise.all([
			api.getScene(saveId),
			api.getResearch(saveId),
		]);
		game.scene = scene;
		game.research = research;
		onSceneLoaded();
	} catch (e) {
		game.error = e instanceof Error ? e.message : 'Failed to load game';
	} finally {
		game.loading = false;
	}
}

export async function chooseOption(choiceIndex: number) {
	if (!game.saveId) return;
	game.loading = true;
	game.error = null;
	try {
		const scene = await api.makeChoice(game.saveId, choiceIndex);
		game.scene = scene;
		// Refresh research items
		game.research = await api.getResearch(game.saveId);
		onSceneLoaded();
	} catch (e) {
		game.error = e instanceof Error ? e.message : 'Failed to make choice';
	} finally {
		game.loading = false;
	}
}

export function advanceDialogue() {
	if (!game.scene?.dialogue) return;

	if (sceneState.dialogueIndex === null) {
		// Move from narrative text to first dialogue line
		sceneState.dialogueIndex = 0;
	} else if (sceneState.dialogueIndex < game.scene.dialogue.length - 1) {
		// Advance to next dialogue line
		sceneState.dialogueIndex++;
	} else {
		// All dialogue shown — reveal choices
		sceneState.showChoices = true;
	}
}

export async function continueToNextChapter() {
	if (!game.saveId) return;
	game.loading = true;
	game.error = null;
	try {
		const scene = await api.advanceChapter(game.saveId);
		game.scene = scene;
		game.research = await api.getResearch(game.saveId);
		onSceneLoaded();
	} catch (e) {
		game.error = e instanceof Error ? e.message : 'Failed to advance chapter';
	} finally {
		game.loading = false;
	}
}

export function toggleResearch() {
	game.showResearch = !game.showResearch;
}
