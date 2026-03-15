<script>
	import { goto } from '$app/navigation';
	import { getState, resetGame } from '$lib/game-state.svelte.js';
	import { formatHours } from '$lib/billable.js';

	let state = $derived(getState());

	let score = $derived(state.scoreResult?.score);
	let ruling = $derived(state.scoreResult?.ruling);
	let details = $derived(state.scoreResult?.details);

	function gradeColor(grade) {
		const colors = { A: '#4caf50', B: '#8bc34a', C: '#ff9800', D: '#ff5722', F: '#f44336' };
		return colors[grade] || 'var(--color-text)';
	}

	function categoryLabel(key) {
		const labels = {
			relevance: 'Relevance',
			strength: 'Strength',
			completeness: 'Completeness',
			efficiency: 'Efficiency',
		};
		return labels[key] || key;
	}

	function categoryMax(key) {
		const maxes = { relevance: 30, strength: 30, completeness: 25, efficiency: 15 };
		return maxes[key] || 0;
	}

	function handlePlayAgain() {
		resetGame();
		goto('/');
	}
</script>

{#if score && ruling}
	<div class="container score-page">
		<div class="grade-display">
			<div class="grade-circle" style="border-color: {gradeColor(score.grade)}">
				<span class="grade-letter" style="color: {gradeColor(score.grade)}">{score.grade}</span>
				<span class="grade-total">{score.total}/100</span>
			</div>
		</div>

		<div class="card ruling-card">
			<h2>The Ruling</h2>
			<p class="judge-name">{ruling.judge_name}</p>
			<p class="ruling-text">"{ruling.ruling}"</p>
		</div>

		<div class="card partner-note">
			<h3>From the Partner's Desk</h3>
			<p>"{ruling.partner_note}"</p>
		</div>

		<div class="score-breakdown">
			<h2>Score Breakdown</h2>
			<div class="score-bars">
				{#each ['relevance', 'strength', 'completeness', 'efficiency'] as category}
					<div class="score-row">
						<span class="score-category">{categoryLabel(category)}</span>
						<div class="score-bar-track">
							<div
								class="score-bar-fill"
								style="width: {(score[category] / categoryMax(category)) * 100}%"
							></div>
						</div>
						<span class="score-value">{score[category]}/{categoryMax(category)}</span>
					</div>
				{/each}
			</div>
		</div>

		{#if details?.completeness}
			<div class="card completeness-detail">
				<h3>Completeness Checklist</h3>
				{#each details.completeness as check}
					<div class="check-item" class:met={check.met}>
						<span class="check-icon">{check.met ? '✓' : '✗'}</span>
						<span class="check-desc">{check.description}</span>
						<span class="check-points">{check.met ? `+${check.points}` : '0'}</span>
					</div>
				{/each}
			</div>
		{/if}

		{#if details?.efficiency}
			<div class="card efficiency-detail">
				<h3>Efficiency</h3>
				<p>
					Hours remaining: <strong>{formatHours(details.efficiency.hours_remaining)}</strong>
					of {formatHours(details.efficiency.total_budget)}
					({Math.round(details.efficiency.fraction * 100)}% remaining)
				</p>
			</div>
		{/if}

		<div class="play-again">
			<button class="btn-primary btn-large" onclick={handlePlayAgain}>
				Play Again
			</button>
		</div>
	</div>
{:else}
	<div class="container">
		<p>No score data. <a href="/">Return to home</a>.</p>
	</div>
{/if}

<style>
	.score-page {
		max-width: 720px;
		margin: 0 auto;
		padding-top: 2rem;
		padding-bottom: 3rem;
	}

	.grade-display {
		text-align: center;
		margin-bottom: 2rem;
	}

	.grade-circle {
		display: inline-flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 120px;
		height: 120px;
		border: 4px solid;
		border-radius: 50%;
		background: var(--color-surface);
	}

	.grade-letter {
		font-family: var(--font-ui);
		font-size: 2.5rem;
		font-weight: 800;
		line-height: 1;
	}

	.grade-total {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-text-muted);
	}

	.ruling-card {
		margin-bottom: 1.5rem;
	}

	.ruling-card h2 {
		font-size: 1.2rem;
		margin-bottom: 0.5rem;
	}

	.judge-name {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		font-style: italic;
		margin-bottom: 0.75rem;
	}

	.ruling-text {
		font-style: italic;
		line-height: 1.8;
		font-size: 1.05rem;
	}

	.partner-note {
		margin-bottom: 2rem;
		background: var(--color-surface-light);
	}

	.partner-note h3 {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.partner-note p {
		font-style: italic;
	}

	.score-breakdown {
		margin-bottom: 2rem;
	}

	.score-breakdown h2 {
		font-size: 1.1rem;
		margin-bottom: 1rem;
	}

	.score-bars {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.score-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.score-category {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		width: 110px;
		color: var(--color-text-muted);
	}

	.score-bar-track {
		flex: 1;
		height: 12px;
		background: var(--color-bg);
		border-radius: 6px;
		overflow: hidden;
	}

	.score-bar-fill {
		height: 100%;
		background: var(--color-accent);
		border-radius: 6px;
		transition: width 0.5s ease;
	}

	.score-value {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		width: 50px;
		text-align: right;
	}

	.completeness-detail, .efficiency-detail {
		margin-bottom: 1.5rem;
	}

	.completeness-detail h3, .efficiency-detail h3 {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		margin-bottom: 0.75rem;
	}

	.check-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0;
		font-family: var(--font-ui);
		font-size: 0.85rem;
	}

	.check-icon {
		width: 1.5rem;
		text-align: center;
		font-weight: 700;
	}

	.check-item.met .check-icon {
		color: var(--color-success);
	}

	.check-item:not(.met) .check-icon {
		color: var(--color-danger);
	}

	.check-desc {
		flex: 1;
	}

	.check-points {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.check-item.met .check-points {
		color: var(--color-success);
	}

	.play-again {
		text-align: center;
		margin-top: 2rem;
	}

	.btn-large {
		padding: 0.75rem 2rem;
		font-size: 1.1rem;
	}
</style>
