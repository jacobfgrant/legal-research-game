<script>
	import { getState, spendHours, collectAuthority, setCurrentDetail } from '$lib/game-state.svelte.js';
	import { getCase, getStatute } from '$lib/api.js';

	let { caseData, scenarioId } = $props();
	let state = $derived(getState());

	let loadingCitation = $state(null);

	function isAlreadyCollected(id) {
		return state.collectedAuthorities.some(a => a.id === id);
	}

	async function handleCitationClick(citedId) {
		if (loadingCitation) return;

		// Following a citation to something already collected is free
		if (!isAlreadyCollected(citedId)) {
			if (!spendHours('follow_citation')) return;
		}

		loadingCitation = citedId;
		try {
			let detail;
			if (isStatute) {
				detail = await getStatute(scenarioId, citedId);
				detail._type = 'statute';
			} else {
				detail = await getCase(scenarioId, citedId);
				detail._type = 'case';
			}
			collectAuthority({
				id: detail.id,
				type: detail._type,
				name: detail._type === 'case' ? detail.name : detail.title,
				citation: detail.citation,
				title: detail.title,
				court: detail.court,
				year: detail.year,
			});
			setCurrentDetail(detail);
		} catch (e) {
			console.error('Failed to load citation:', e);
		} finally {
			loadingCitation = null;
		}
	}

	function citationName(citedId) {
		if (citedId.startsWith('statute_')) return citedId.replace('_', ' ');
		return citedId.replace('_', ' ');
	}
</script>

<div class="case-detail">
	<div class="detail-header">
		<h2>{caseData.name}</h2>
		<div class="detail-meta">
			<span>{caseData.citation}</span>
			<span>{caseData.court}</span>
			{#if caseData.overruled}
				<span class="overruled-badge">OVERRULED</span>
			{/if}
		</div>
	</div>

	<section>
		<h3>Facts</h3>
		{#each caseData.facts.split('\n\n') as paragraph}
			<p>{paragraph}</p>
		{/each}
	</section>

	<section>
		<h3>Holding</h3>
		{#each caseData.holding.split('\n\n') as paragraph}
			<p>{paragraph}</p>
		{/each}
	</section>

	<section>
		<h3>Reasoning</h3>
		{#each caseData.reasoning.split('\n\n') as paragraph}
			<p>{paragraph}</p>
		{/each}
	</section>

	{#if caseData.citations.length > 0}
		<section class="citations-section">
			<h3>Citations ({state.scenario?.costs.follow_citation} hrs each)</h3>
			<div class="citation-links">
				{#each caseData.citations as citedId}
					<button
						class="btn-secondary citation-btn"
						disabled={!state.canFollowCitation || loadingCitation === citedId}
						onclick={() => handleCitationClick(citedId)}
					>
						{loadingCitation === citedId ? 'Loading...' : citationName(citedId)}
					</button>
				{/each}
			</div>
		</section>
	{/if}

	{#if caseData.cited_by.length > 0}
		<section class="citations-section">
			<h3>Cited By ({state.scenario?.costs.follow_citation} hrs each)</h3>
			<div class="citation-links">
				{#each caseData.cited_by as citedId}
					<button
						class="btn-secondary citation-btn"
						disabled={!state.canFollowCitation || loadingCitation === citedId}
						onclick={() => handleCitationClick(citedId)}
					>
						{loadingCitation === citedId ? 'Loading...' : citationName(citedId)}
					</button>
				{/each}
			</div>
		</section>
	{/if}
</div>

<style>
	.case-detail {
		line-height: 1.7;
		color: var(--color-text);
	}

	.detail-header {
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid var(--color-text-dim);
	}

	.detail-header h2 {
		font-size: 1.3rem;
		margin-bottom: 0.3rem;
	}

	.detail-meta {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.overruled-badge {
		background: var(--color-danger);
		color: white;
		padding: 0.1rem 0.4rem;
		border-radius: 3px;
		font-size: 0.75rem;
		font-weight: 700;
	}

	section {
		margin-bottom: 1.25rem;
	}

	h3 {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	p {
		margin-bottom: 0.6rem;
	}

	.citations-section {
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px solid var(--color-text-dim);
	}

	.citation-links {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.citation-btn {
		font-size: 0.8rem;
		padding: 0.3rem 0.6rem;
	}
</style>
