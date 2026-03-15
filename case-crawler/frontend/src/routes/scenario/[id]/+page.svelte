<script>
	import { goto } from '$app/navigation';
	import { getState, beginResearch } from '$lib/game-state.svelte.js';

	let state = $derived(getState());

	function handleBeginResearch() {
		beginResearch();
		goto(`/research/${state.scenario.id}`);
	}
</script>

{#if state.scenario}
	<div class="container briefing">
		<div class="card memo-header">
			<div class="memo-from">
				<span class="label">FROM:</span>
				<span>{state.scenario.assignment.partner_name}, Partner</span>
			</div>
			<div class="memo-re">
				<span class="label">RE:</span>
				<span>{state.scenario.assignment.client_name} — {state.scenario.title}</span>
			</div>
			<div class="memo-court">
				<span class="label">COURT:</span>
				<span>{state.scenario.court}, {state.scenario.jurisdiction}</span>
			</div>
		</div>

		<div class="card assignment">
			<h2>The Assignment</h2>
			{#each state.scenario.assignment.fact_pattern.split('\n\n') as paragraph}
				<p>{paragraph}</p>
			{/each}
		</div>

		<div class="card issue">
			<h3>Legal Issue</h3>
			<p class="issue-text">{state.scenario.assignment.legal_issue}</p>
			<h3>Your Position</h3>
			<p class="position-text">{state.scenario.assignment.your_position}</p>
		</div>

		<div class="card budget">
			<h3>Research Budget</h3>
			<p>
				You have <strong>{state.scenario.billable_hours} billable hours</strong> to research this issue.
				Every action costs time:
			</p>
			<ul>
				<li>Keyword search: <strong>{state.scenario.costs.search} hrs</strong></li>
				<li>Read a case: <strong>{state.scenario.costs.read_case} hrs</strong></li>
				<li>Read a statute: <strong>{state.scenario.costs.read_statute} hrs</strong></li>
				<li>Follow a citation: <strong>{state.scenario.costs.follow_citation} hrs</strong></li>
			</ul>
			<p class="budget-note">Research efficiently. Unused hours improve your score.</p>
		</div>

		<div class="start-action">
			<button class="btn-primary btn-large" onclick={handleBeginResearch}>
				Begin Research
			</button>
		</div>
	</div>
{:else}
	<div class="container">
		<p>No scenario loaded. <a href="/">Return to home</a>.</p>
	</div>
{/if}

<style>
	.briefing {
		max-width: 720px;
		margin: 0 auto;
		padding-top: 2rem;
		padding-bottom: 3rem;
	}

	.memo-header {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		margin-bottom: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.label {
		color: var(--color-text-muted);
		display: inline-block;
		width: 60px;
		font-weight: 700;
	}

	.assignment {
		margin-bottom: 1.5rem;
	}

	.assignment h2 {
		margin-bottom: 1rem;
		color: var(--color-accent);
	}

	.assignment p {
		margin-bottom: 0.75rem;
	}

	.issue {
		margin-bottom: 1.5rem;
	}

	.issue h3 {
		font-size: 0.9rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.4rem;
		margin-top: 1rem;
	}

	.issue h3:first-child {
		margin-top: 0;
	}

	.issue-text {
		font-style: italic;
		font-size: 1.05rem;
	}

	.position-text {
		color: var(--color-accent);
		font-weight: 600;
	}

	.budget {
		margin-bottom: 2rem;
	}

	.budget h3 {
		margin-bottom: 0.75rem;
	}

	.budget ul {
		list-style: none;
		padding-left: 1rem;
		margin: 0.75rem 0;
		font-family: var(--font-ui);
		font-size: 0.9rem;
	}

	.budget li {
		margin-bottom: 0.3rem;
	}

	.budget li::before {
		content: '·';
		margin-right: 0.5rem;
		color: var(--color-text-dim);
	}

	.budget-note {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		font-style: italic;
	}

	.start-action {
		text-align: center;
	}

	.btn-large {
		padding: 0.75rem 2rem;
		font-size: 1.1rem;
	}
</style>
