<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listScenarios, createSession, getScenario } from '$lib/api.js';
	import { startScenario, getState } from '$lib/game-state.svelte.js';

	let scenarios = $state([]);
	let loading = $state(true);
	let starting = $state(false);
	let error = $state(null);

	let state = $derived(getState());

	// If there's an active game, redirect to the right phase
	$effect(() => {
		if (state.gamePhase !== 'select' && state.scenario) {
			goto(`/${state.gamePhase}/${state.scenario.id}`);
		}
	});

	onMount(async () => {
		try {
			scenarios = await listScenarios();
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	async function handleStart(scenarioId) {
		starting = true;
		error = null;
		try {
			const [scenarioData, session] = await Promise.all([
				getScenario(scenarioId),
				createSession(scenarioId),
			]);
			startScenario(scenarioData, session.session_id);
			goto(`/scenario/${scenarioId}`);
		} catch (e) {
			error = e.message;
			starting = false;
		}
	}
</script>

<div class="container home">
	<div class="hero">
		<h1>Case Crawler</h1>
		<p class="subtitle">Legal Research Puzzle Game</p>
		<p class="tagline">Search. Cite. Argue. Win.</p>
	</div>

	{#if loading}
		<p class="loading">Loading scenarios...</p>
	{:else if error}
		<p class="error">{error}</p>
	{:else}
		<div class="scenarios">
			<h2>Select a Scenario</h2>
			{#each scenarios as s}
				<div class="card scenario-card">
					<div class="scenario-header">
						<h3>{s.title}</h3>
						<span class="tag">{s.difficulty}</span>
					</div>
					<p class="scenario-jurisdiction">{s.jurisdiction}</p>
					<button
						class="btn-primary"
						disabled={starting}
						onclick={() => handleStart(s.id)}
					>
						{starting ? 'Starting...' : 'Take the Case'}
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.home {
		padding-top: 3rem;
	}

	.hero {
		text-align: center;
		margin-bottom: 3rem;
	}

	.hero h1 {
		font-size: 2.5rem;
		color: var(--color-accent);
		margin-bottom: 0.25rem;
	}

	.subtitle {
		font-family: var(--font-ui);
		font-size: 1.1rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.tagline {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		color: var(--color-text-dim);
	}

	.scenarios {
		max-width: 600px;
		margin: 0 auto;
	}

	.scenarios h2 {
		margin-bottom: 1rem;
		font-size: 1.2rem;
		color: var(--color-text-muted);
	}

	.scenario-card {
		margin-bottom: 1rem;
	}

	.scenario-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.5rem;
	}

	.scenario-header h3 {
		font-size: 1.1rem;
	}

	.scenario-jurisdiction {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		margin-bottom: 1rem;
	}

	.loading, .error {
		text-align: center;
		font-family: var(--font-ui);
		color: var(--color-text-muted);
	}

	.error {
		color: var(--color-danger);
	}
</style>
