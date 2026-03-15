<script>
	let { caseData, onclick, active = false } = $props();
</script>

<button
	class="case-card"
	class:active
	{onclick}
>
	<div class="case-name">{caseData.name}</div>
	<div class="case-meta">
		<span class="case-citation">{caseData.citation}</span>
		<span class="case-court">{caseData.court}</span>
	</div>
	<div class="case-tags">
		{#each caseData.tags.slice(0, 4) as tag}
			<span class="tag">{tag}</span>
		{/each}
	</div>
</button>

<style>
	.case-card {
		display: block;
		width: 100%;
		text-align: left;
		background: var(--color-surface);
		border: 1px solid var(--color-text-dim);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		margin-bottom: 0.5rem;
		cursor: pointer;
		transition: border-color 0.2s, background 0.2s;
	}

	.case-card:hover {
		border-color: var(--color-accent);
		background: var(--color-surface-light);
	}

	.case-card.active {
		border-color: var(--color-accent);
		background: var(--color-surface-light);
	}

	.case-name {
		font-family: var(--font-ui);
		font-weight: 600;
		font-size: 0.95rem;
		margin-bottom: 0.25rem;
	}

	.case-meta {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-bottom: 0.4rem;
	}

	.case-citation {
		margin-right: 0.75rem;
	}

	.case-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}
</style>
