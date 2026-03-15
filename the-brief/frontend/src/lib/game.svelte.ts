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
	/** Whether the player has finished interacting with the scene */
	showChoices: false,
	/** Whether to show a chapter title card */
	showChapterTitle: false,
	/** The chapter title being displayed */
	chapterTitleText: '',
	/** Track current chapter to detect transitions */
	currentChapter: '',
});

function resetSceneState() {
	sceneState.dialogueIndex = null;
	sceneState.showChoices = false;
}

function onSceneLoaded() {
	resetSceneState();

	const scene = game.scene;
	if (!scene) return;

	// Detect chapter transition — show title card
	if (scene.chapter_title && scene.chapter_title !== sceneState.chapterTitleText) {
		sceneState.chapterTitleText = scene.chapter_title;
		if (sceneState.currentChapter && sceneState.currentChapter !== scene.chapter_title) {
			// Chapter changed mid-session — show title card
			sceneState.showChapterTitle = true;
			setTimeout(() => {
				sceneState.showChapterTitle = false;
			}, 2500);
		}
		sceneState.currentChapter = scene.chapter_title;
	}

	// If no dialogue, show choices/terminal state immediately
	if (!scene.dialogue?.length) {
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
		// Show title card for first chapter
		sceneState.currentChapter = '';
		sceneState.chapterTitleText = '';
		onSceneLoaded();
		sceneState.showChapterTitle = true;
		setTimeout(() => {
			sceneState.showChapterTitle = false;
		}, 2500);
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
		// Don't show title card on load — player is resuming
		sceneState.currentChapter = scene.chapter_title;
		sceneState.chapterTitleText = scene.chapter_title;
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
		sceneState.dialogueIndex = 0;
	} else if (sceneState.dialogueIndex < game.scene.dialogue.length - 1) {
		sceneState.dialogueIndex++;
	} else {
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
