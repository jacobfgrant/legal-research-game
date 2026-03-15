<script>
	import { getState, spendHours, collectAuthority, setCurrentDetail } from '$lib/game-state.svelte.js';
	import { getCase, getStatute } from '$lib/api.js';

	let { statuteData, scenarioId } = $props();
	let state = $derived(getState());
	let loadingCitation = $state(null);

	function isAlreadyCollected(id) {
		return state.collectedAuthorities.some(a => a.id === id);
	}

	async function handleCitedByClick(citedId) {
		if (loadingCitation) return;
		if (!isAlreadyCollected(citedId)) {
			if (!spendHours('follow_citation')) return;
		}

		loadingCitation = citedId;
		try {
			const detail = await getCase(scenarioId, citedId);
			detail._type = 'case';
			collectAuthority({
				id: detail.id,
				type: 'case',
				name: detail.name,
				citation: detail.citation,
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
</script>

<div class="statute-detail">
	<div class="detail-header">
		<h2>{statuteData.title}</h2>
		<div class="detail-meta">
			<span>{statuteData.jurisdiction}</span>
			<span>Effective: {statuteData.effective_date}</span>
		</div>
	</div>

	<section class="statute-text">
		{#each statuteData.text.split('\n\n') as paragraph}
			<p>{paragraph}</p>
		{/each}
	</section>

	{#if statuteData.cited_by.length > 0}
		<section class="citations-section">
			<h3>Cases Citing This Statute ({state.scenario?.costs.follow_citation} hrs each)</h3>
			<div class="citation-links">
				{#each statuteData.cited_by as citedId}
					<button
						class="btn-secondary citation-btn"
						disabled={!state.canFollowCitation || loadingCitation === citedId}
						onclick={() => handleCitedByClick(citedId)}
					>
						{loadingCitation === citedId ? 'Loading...' : citedId.replace('_', ' ')}
					</button>
				{/each}
			</div>
		</section>
	{/if}
</div>

<style>
	.statute-detail {
		line-height: 1.7;
		color: var(--color-text);
	}

	.detail-header {
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid var(--color-text-dim);
	}

	.detail-header h2 {
		font-size: 1.2rem;
		margin-bottom: 0.3rem;
	}

	.detail-meta {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		display: flex;
		gap: 1rem;
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

	.statute-text p {
		margin-bottom: 0.6rem;
		white-space: pre-line;
		color: var(--color-text);
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
