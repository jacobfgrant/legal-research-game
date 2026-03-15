<script>
	import '../app.css';
	import { getState } from '$lib/game-state.svelte.js';
	import { formatHours, hoursColor, hoursFraction } from '$lib/billable.js';

	let { children } = $props();
	let state = $derived(getState());

	let showHours = $derived(
		state.scenario !== null && !['select', 'score'].includes(state.gamePhase)
	);
</script>

<div class="app">
	<header>
		<div class="container header-inner">
			<a href="/" class="logo">Case Crawler</a>
			{#if showHours}
				<div class="hours-display">
					<span class="hours-label">Billable Hours</span>
					<div class="hours-bar">
						<div
							class="hours-fill"
							style="width: {hoursFraction(state.billableHours, state.scenario.billable_hours) * 100}%; background: {hoursColor(state.billableHours, state.scenario.billable_hours)}"
						></div>
					</div>
					<span class="hours-value" style="color: {hoursColor(state.billableHours, state.scenario.billable_hours)}">
						{formatHours(state.billableHours)} / {formatHours(state.scenario.billable_hours)}
					</span>
				</div>
			{/if}
		</div>
	</header>

	<main>
		{@render children()}
	</main>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	header {
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-text-dim);
		padding: 0.6rem 0;
	}

	.header-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1.5rem;
	}

	.logo {
		font-family: var(--font-ui);
		font-size: 1.2rem;
		font-weight: 700;
		color: var(--color-accent);
		text-decoration: none;
		white-space: nowrap;
	}

	.hours-display {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-family: var(--font-ui);
		font-size: 0.85rem;
	}

	.hours-label {
		color: var(--color-text-muted);
		white-space: nowrap;
	}

	.hours-bar {
		width: 120px;
		height: 8px;
		background: var(--color-bg);
		border-radius: 4px;
		overflow: hidden;
	}

	.hours-fill {
		height: 100%;
		border-radius: 4px;
		transition: width 0.3s ease, background 0.3s ease;
	}

	.hours-value {
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}

	main {
		flex: 1;
	}
</style>
