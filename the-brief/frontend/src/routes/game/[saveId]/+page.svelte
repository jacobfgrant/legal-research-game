<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { fade, fly, slide } from 'svelte/transition';
	import {
		game,
		sceneState,
		loadExistingGame,
		chooseOption,
		advanceDialogue,
		continueToNextChapter,
		toggleResearch,
	} from '$lib/game.svelte';

	onMount(() => {
		const saveId = page.params.saveId;
		if (game.saveId !== saveId || !game.scene) {
			loadExistingGame(saveId);
		}
	});

	function handleClick() {
		if (game.scene?.dialogue && !sceneState.showChoices) {
			advanceDialogue();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === ' ' || e.key === 'Enter') {
			if (game.scene?.dialogue && !sceneState.showChoices) {
				e.preventDefault();
				advanceDialogue();
			}
		}
		if (e.key === 'Escape' && game.showResearch) {
			toggleResearch();
		}
	}

	function actColor(act: string): string {
		switch (act) {
			case 'setup':
				return 'var(--color-act-setup)';
			case 'research':
				return 'var(--color-act-research)';
			case 'outcome':
				return 'var(--color-act-outcome)';
			default:
				return 'var(--color-accent)';
		}
	}

	function actBg(act: string): string {
		switch (act) {
			case 'setup':
				return 'rgba(201, 168, 76, 0.04)';
			case 'research':
				return 'rgba(92, 138, 175, 0.06)';
			case 'outcome':
				return 'rgba(175, 92, 122, 0.06)';
			default:
				return 'transparent';
		}
	}

	function typeColor(type: string): string {
		switch (type) {
			case 'statute':
				return 'var(--color-act-setup)';
			case 'case':
				return 'var(--color-act-research)';
			case 'document':
				return 'var(--color-act-outcome)';
			default:
				return 'var(--color-accent)';
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Chapter title card overlay -->
{#if sceneState.showChapterTitle && game.scene}
	<div class="chapter-title-card" in:fade={{ duration: 500 }} out:fade={{ duration: 500 }}>
		<p class="chapter-label">Chapter</p>
		<h1 class="chapter-name">{game.scene.chapter_title}</h1>
	</div>
{/if}

{#if game.loading && !game.scene}
	<div class="game-container">
		<div class="loading-container" in:fade>
			<p class="loading">Loading...</p>
		</div>
	</div>
{:else if game.error && !game.scene}
	<div class="game-container">
		<div class="error-container" in:fade>
			<p class="error">{game.error}</p>
			<a href="/" class="back-link">Back to menu</a>
		</div>
	</div>
{:else if game.scene}
	{@const scene = game.scene}
	{@const accent = actColor(scene.act)}

	<div
		class="game-container"
		class:is-loading={game.loading}
		style="--act-color: {accent}; background-color: {actBg(scene.act)}"
	>
		<!-- Top bar -->
		<nav class="top-bar">
			<a href="/" class="back-link">Menu</a>
			<span class="act-label">{scene.act}</span>
			<button
				class="research-toggle"
				class:has-items={game.research.length > 0}
				onclick={toggleResearch}
			>
				Research ({game.research.length})
			</button>
		</nav>

		<!-- Main content area — click anywhere to advance dialogue -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<main class="scene" onclick={handleClick}>
			{#key scene.id}
				<div class="scene-content" in:fade={{ duration: 300, delay: 200 }} out:fade={{ duration: 200 }}>
					<!-- Narrative text — always visible -->
					{#if sceneState.dialogueIndex === null}
						<div class="narrative">
							{#each scene.text.split('\n\n') as paragraph}
								{#if paragraph.trim()}
									<p>{paragraph.trim()}</p>
								{/if}
							{/each}
						</div>

						{#if scene.dialogue?.length}
							<p class="continue-hint" in:fade={{ delay: 500 }}>Click to continue</p>
						{/if}
					{/if}

					<!-- Dialogue -->
					{#if sceneState.dialogueIndex !== null && scene.dialogue}
						{@const line = scene.dialogue[sceneState.dialogueIndex]}
						{@const charInfo = scene.character_info[line.character]}

						<div class="dialogue" in:fade={{ duration: 200 }}>
							<span class="speaker" style="color: {accent}">
								{charInfo?.name ?? line.character}
							</span>
							<p class="dialogue-line">"{line.line}"</p>
						</div>

						{#if !sceneState.showChoices}
							<p class="continue-hint" in:fade={{ delay: 400 }}>Click to continue</p>
						{/if}
					{/if}

					<!-- Choices -->
					{#if sceneState.showChoices && scene.choices}
						<div class="choices" in:fly={{ y: 30, duration: 300, delay: 200 }}>
							{#each scene.choices as choice (choice.index)}
								<button
									class="choice-btn"
									disabled={game.loading}
									onclick={() => chooseOption(choice.index)}
								>
									{choice.label}
								</button>
							{/each}
						</div>
					{/if}

					<!-- Chapter end (terminal scene) -->
					{#if scene.terminal && sceneState.showChoices}
						<div class="chapter-end" in:fade={{ delay: 400 }}>
							<p class="end-text">End of Chapter</p>
							{#if scene.has_next_chapter}
								<button
									class="btn-primary"
									disabled={game.loading}
									onclick={continueToNextChapter}
								>
									{game.loading ? 'Loading...' : 'Continue'}
								</button>
							{:else}
								<p class="end-subtext">The story continues...</p>
								<a href="/" class="btn-primary">Return to Menu</a>
							{/if}
						</div>
					{/if}
				</div>
			{/key}
		</main>

		<!-- Research sidebar -->
		{#if game.showResearch}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div class="research-backdrop" onclick={toggleResearch} transition:fade={{ duration: 200 }}></div>
			<aside class="research-panel" transition:slide={{ axis: 'x', duration: 300 }}>
				<div class="research-header">
					<h2>Research</h2>
					<button class="close-btn" onclick={toggleResearch}>Close</button>
				</div>
				{#if game.research.length === 0}
					<p class="dim">No research items found yet.</p>
				{:else}
					<ul class="research-list">
						{#each game.research as item (item.id)}
							<li class="research-item" in:fade>
								<div class="item-meta">
									<span class="item-type" style="color: {typeColor(item.type)}">{item.type}</span>
									{#if item.jurisdiction}
										<span class="item-jurisdiction">{item.jurisdiction}</span>
									{/if}
								</div>
								<h3>{item.name}</h3>
								<p>{item.description}</p>
							</li>
						{/each}
					</ul>
				{/if}
			</aside>
		{/if}
	</div>
{/if}

<style>
	.game-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		position: relative;
		transition: background-color 0.6s ease;
	}

	.game-container.is-loading {
		opacity: 0.7;
		pointer-events: none;
		transition: opacity 0.2s;
	}

	/* Chapter title card */
	.chapter-title-card {
		position: fixed;
		inset: 0;
		z-index: 200;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: var(--color-bg);
		pointer-events: none;
	}

	.chapter-label {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.2em;
		color: var(--color-text-dim);
		margin-bottom: 0.75rem;
	}

	.chapter-name {
		font-family: var(--font-body);
		font-size: 2.5rem;
		font-weight: 400;
		font-style: italic;
		color: var(--color-accent);
		letter-spacing: 0.03em;
	}

	/* Top bar */
	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem var(--spacing);
		border-bottom: 1px solid var(--color-surface);
		font-family: var(--font-ui);
		font-size: 0.85rem;
	}

	.back-link {
		color: var(--color-text-dim);
		font-family: var(--font-ui);
		font-size: 0.85rem;
	}

	.act-label {
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--act-color);
		font-weight: 600;
	}

	.research-toggle {
		font-size: 0.85rem;
		color: var(--color-text-dim);
		padding: 0.25rem 0.75rem;
		border: 1px solid var(--color-surface);
		border-radius: 3px;
		transition:
			border-color 0.2s,
			color 0.2s;
	}

	.research-toggle:hover {
		border-color: var(--color-text-dim);
	}

	.research-toggle.has-items {
		color: var(--color-accent);
		border-color: var(--color-accent-dim);
	}

	/* Scene content */
	.scene {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 3rem var(--spacing);
		cursor: pointer;
	}

	.scene-content {
		max-width: var(--max-width);
		width: 100%;
	}

	/* Narrative */
	.narrative p {
		margin-bottom: 1.25rem;
	}

	.continue-hint {
		text-align: center;
		color: var(--color-text-dim);
		font-family: var(--font-ui);
		font-size: 0.8rem;
		margin-top: 2rem;
		animation: pulse 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 0.4;
		}
		50% {
			opacity: 0.8;
		}
	}

	/* Dialogue */
	.dialogue {
		text-align: center;
		padding: 2rem 0;
	}

	.speaker {
		font-family: var(--font-ui);
		font-size: 0.9rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		display: block;
		margin-bottom: 0.75rem;
	}

	.dialogue-line {
		font-size: 1.25rem;
		font-style: italic;
		max-width: min(600px, 90%);
		margin: 0 auto;
		line-height: 1.8;
	}

	/* Choices */
	.choices {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin-top: 2.5rem;
		cursor: default;
	}

	.choice-btn {
		display: block;
		width: 100%;
		text-align: left;
		padding: 1rem 1.25rem;
		background: var(--color-surface);
		border: 1px solid transparent;
		border-radius: 4px;
		font-family: var(--font-body);
		font-size: 1rem;
		line-height: 1.5;
		color: var(--color-text);
		transition:
			border-color 0.2s,
			background 0.2s;
	}

	.choice-btn:hover:not(:disabled) {
		border-color: var(--act-color);
		background: var(--color-bg-light);
	}

	.choice-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Chapter end */
	.chapter-end {
		text-align: center;
		margin-top: 3rem;
		padding-top: 2rem;
		border-top: 1px solid var(--color-surface);
	}

	.end-text {
		font-family: var(--font-ui);
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--color-text-dim);
		margin-bottom: 1.5rem;
	}

	.end-subtext {
		font-family: var(--font-body);
		font-style: italic;
		color: var(--color-text-dim);
		margin-bottom: 1.5rem;
	}

	.btn-primary {
		display: inline-block;
		font-family: var(--font-ui);
		font-size: 1rem;
		padding: 0.625rem 1.5rem;
		background: var(--color-accent);
		color: var(--color-bg);
		border-radius: 4px;
		font-weight: 600;
		transition: background 0.2s;
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--color-accent-dim);
		text-decoration: none;
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Research sidebar */
	.research-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.4);
		z-index: 99;
	}

	.research-panel {
		position: fixed;
		top: 0;
		right: 0;
		width: min(380px, 90vw);
		height: 100vh;
		background: var(--color-bg-light);
		border-left: 1px solid var(--color-surface);
		padding: var(--spacing);
		overflow-y: auto;
		z-index: 100;
	}

	.research-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}

	.research-header h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-text-dim);
	}

	.close-btn {
		font-size: 0.85rem;
		color: var(--color-text-dim);
		padding: 0.25rem 0.5rem;
	}

	.close-btn:hover {
		color: var(--color-text);
	}

	.research-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.research-item {
		padding: 1rem;
		background: var(--color-surface);
		border-radius: 4px;
	}

	.item-meta {
		margin-bottom: 0.5rem;
	}

	.research-item h3 {
		font-family: var(--font-body);
		font-size: 1rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.research-item p {
		font-size: 0.9rem;
		color: var(--color-text-dim);
		line-height: 1.5;
	}

	.item-type {
		font-family: var(--font-ui);
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		margin-right: 0.5rem;
	}

	.item-jurisdiction {
		font-family: var(--font-ui);
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-text-dim);
	}

	.dim {
		color: var(--color-text-dim);
		font-size: 0.9rem;
	}

	.loading-container,
	.error-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		padding: 3rem;
		font-family: var(--font-ui);
	}

	.loading {
		color: var(--color-text-dim);
	}

	.error {
		color: var(--color-error);
	}

	/* Mobile */
	@media (max-width: 600px) {
		.scene {
			padding: 2rem 1rem;
		}

		.chapter-name {
			font-size: 1.75rem;
		}

		.dialogue-line {
			font-size: 1.1rem;
		}
	}
</style>
