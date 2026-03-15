<script>
	import { goto } from '$app/navigation';
	import { getState } from '$lib/game-state.svelte.js';

	let state = $derived(getState());

	let revealedCount = $state(0);
	let allRevealed = $derived(
		state.rebuttalData && revealedCount >= state.rebuttalData.arguments.length
	);

	function revealNext() {
		if (state.rebuttalData && revealedCount < state.rebuttalData.arguments.length) {
			revealedCount++;
		}
	}

	function handleSeeRuling() {
		goto(`/score/${state.scenario.id}`);
	}
</script>

{#if state.rebuttalData && state.scenario}
	<div class="container rebuttal-page">
		<div class="rebuttal-header">
			<h1>Opposition Rebuttal</h1>
			<p class="counsel-name">{state.rebuttalData.opposing_counsel}, Counsel for Plaintiff</p>
		</div>

		<div class="card intro">
			<p class="intro-text">{state.rebuttalData.intro}</p>
		</div>

		<div class="arguments">
			{#each state.rebuttalData.arguments as arg, i}
				{#if i < revealedCount}
					<div class="card argument-card" class:strong={arg.strength === 'strong'}>
						<div class="arg-header">
							<span class="arg-type">
								{arg.type === 'cite_case' ? 'Cites Authority' : 'Distinguishes Your Case'}
							</span>
							<span class="arg-strength strength-{arg.strength}">{arg.strength}</span>
						</div>
						<p class="arg-summary">{arg.summary}</p>
					</div>
				{/if}
			{/each}
		</div>

		{#if !allRevealed}
			<div class="reveal-action">
				<button class="btn-primary" onclick={revealNext}>
					{revealedCount === 0 ? 'Hear Opposition' : 'Continue'}
				</button>
			</div>
		{:else}
			<div class="card closing">
				<p class="closing-text">"{state.rebuttalData.closing}"</p>
			</div>
			<div class="ruling-action">
				<p class="ruling-prompt">The court will now rule.</p>
				<button class="btn-primary btn-large" onclick={handleSeeRuling}>
					See the Ruling
				</button>
			</div>
		{/if}
	</div>
{:else}
	<div class="container">
		<p>No rebuttal data. <a href="/">Return to home</a>.</p>
	</div>
{/if}

<style>
	.rebuttal-page {
		max-width: 720px;
		margin: 0 auto;
		padding-top: 2rem;
		padding-bottom: 3rem;
	}

	.rebuttal-header {
		margin-bottom: 1.5rem;
	}

	.rebuttal-header h1 {
		font-size: 1.5rem;
		margin-bottom: 0.25rem;
	}

	.counsel-name {
		font-family: var(--font-ui);
		font-size: 0.9rem;
		color: var(--color-text-muted);
		font-style: italic;
	}

	.intro {
		margin-bottom: 1.5rem;
	}

	.intro-text {
		font-style: italic;
		color: var(--color-text-muted);
	}

	.arguments {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.argument-card {
		border-left: 3px solid var(--color-text-dim);
	}

	.argument-card.strong {
		border-left-color: var(--color-danger);
	}

	.arg-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.arg-type {
		font-family: var(--font-ui);
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
	}

	.arg-strength {
		font-family: var(--font-ui);
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		padding: 0.1rem 0.4rem;
		border-radius: 3px;
	}

	.strength-strong {
		background: rgba(244, 67, 54, 0.2);
		color: var(--color-danger);
	}

	.strength-moderate {
		background: rgba(255, 152, 0, 0.2);
		color: var(--color-warning);
	}

	.reveal-action {
		text-align: center;
		margin: 2rem 0;
	}

	.closing {
		margin-bottom: 2rem;
		background: var(--color-surface-light);
	}

	.closing-text {
		font-style: italic;
		line-height: 1.8;
	}

	.ruling-action {
		text-align: center;
	}

	.ruling-prompt {
		font-family: var(--font-ui);
		font-size: 1.1rem;
		color: var(--color-text-muted);
		margin-bottom: 1rem;
	}

	.btn-large {
		padding: 0.75rem 2rem;
		font-size: 1.1rem;
	}
</style>
