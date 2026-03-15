<script lang="ts">
	import { onMount } from 'svelte';
	import { startNewGame } from '$lib/game.svelte';
	import * as api from '$lib/api';
	import type { SaveSummary } from '$lib/types';

	let saves = $state<SaveSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			saves = await api.listSaves();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load saves';
		} finally {
			loading = false;
		}
	});

	async function handleDelete(saveId: string) {
		try {
			await api.deleteSave(saveId);
			saves = saves.filter((s) => s.save_id !== saveId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete save';
		}
	}

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		});
	}
</script>

<div class="menu">
	<header>
		<h1>The Brief</h1>
		<p class="subtitle">A Legal Research Game</p>
	</header>

	<div class="actions">
		<button class="btn-primary" onclick={startNewGame}>New Game</button>
	</div>

	{#if error}
		<p class="error">{error}</p>
	{/if}

	{#if loading}
		<p class="dim">Loading...</p>
	{:else if saves.length > 0}
		<section class="saves">
			<h2>Continue</h2>
			<ul>
				{#each saves as save (save.save_id)}
					<li>
						<a href="/game/{save.save_id}" class="save-link">
							<span class="save-chapter">{save.current_chapter}</span>
							<span class="save-scene">{save.current_scene}</span>
							<span class="save-date">{formatDate(save.updated_at)}</span>
						</a>
						<button class="btn-delete" onclick={() => handleDelete(save.save_id)}>
							Delete
						</button>
					</li>
				{/each}
			</ul>
		</section>
	{/if}
</div>

<style>
	.menu {
		max-width: var(--max-width);
		margin: 0 auto;
		padding: var(--spacing);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		gap: 2rem;
	}

	header {
		text-align: center;
	}

	h1 {
		font-family: var(--font-body);
		font-size: 3rem;
		font-weight: 400;
		font-style: italic;
		color: var(--color-accent);
		letter-spacing: 0.05em;
	}

	.subtitle {
		color: var(--color-text-dim);
		font-size: 1rem;
		margin-top: 0.5rem;
		font-family: var(--font-ui);
		text-transform: uppercase;
		letter-spacing: 0.15em;
	}

	.actions {
		display: flex;
		gap: 1rem;
	}

	.btn-primary {
		font-family: var(--font-ui);
		font-size: 1.125rem;
		padding: 0.75rem 2rem;
		background: var(--color-accent);
		color: var(--color-bg);
		border-radius: 4px;
		font-weight: 600;
		transition: background 0.2s;
	}

	.btn-primary:hover {
		background: var(--color-accent-dim);
	}

	.saves {
		width: 100%;
		max-width: 500px;
	}

	.saves h2 {
		font-size: 1rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-text-dim);
		margin-bottom: 0.75rem;
	}

	.saves ul {
		list-style: none;
	}

	.saves li {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 0;
		border-bottom: 1px solid var(--color-surface);
	}

	.save-link {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
	}

	.save-chapter {
		font-family: var(--font-ui);
		font-size: 0.9rem;
		color: var(--color-text);
	}

	.save-scene {
		font-family: var(--font-ui);
		font-size: 0.8rem;
		color: var(--color-text-dim);
	}

	.save-date {
		font-family: var(--font-ui);
		font-size: 0.75rem;
		color: var(--color-text-dim);
	}

	.btn-delete {
		font-size: 0.8rem;
		color: var(--color-text-dim);
		padding: 0.25rem 0.5rem;
		transition: color 0.2s;
	}

	.btn-delete:hover {
		color: var(--color-error);
	}

	.error {
		color: var(--color-error);
		font-family: var(--font-ui);
		font-size: 0.9rem;
	}

	.dim {
		color: var(--color-text-dim);
	}
</style>
