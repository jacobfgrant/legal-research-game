<script>
	import { goto } from '$app/navigation';
	import { searchAuthorities, getCase, getStatute } from '$lib/api.js';
	import {
		getState, spendHours, collectAuthority, setCurrentDetail,
		logSearch, goToArgument
	} from '$lib/game-state.svelte.js';
	import GameGuard from '$lib/components/GameGuard.svelte';
	import CaseCard from '$lib/components/CaseCard.svelte';
	import CaseDetail from '$lib/components/CaseDetail.svelte';
	import StatuteDetail from '$lib/components/StatuteDetail.svelte';

	let state = $derived(getState());

	let query = $state('');
	let searchResults = $state({ cases: [], statutes: [] });
	let searching = $state(false);
	let loadingDetail = $state(false);
	let showCollected = $state(false);

	let hasResults = $derived(
		searchResults.cases.length > 0 || searchResults.statutes.length > 0
	);

	async function handleSearch(e) {
		e.preventDefault();
		if (!query.trim() || searching) return;
		if (!spendHours('search')) return;

		searching = true;
		try {
			searchResults = await searchAuthorities(state.scenario.id, query);
			logSearch(query, searchResults.cases.length + searchResults.statutes.length);
		} catch (err) {
			console.error('Search failed:', err);
		} finally {
			searching = false;
		}
	}

	async function handleReadCase(caseId) {
		if (loadingDetail) return;
		if (!spendHours('read_case')) return;

		loadingDetail = true;
		try {
			const detail = await getCase(state.scenario.id, caseId);
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
		} catch (err) {
			console.error('Failed to load case:', err);
		} finally {
			loadingDetail = false;
		}
	}

	async function handleReadStatute(statuteId) {
		if (loadingDetail) return;
		if (!spendHours('read_statute')) return;

		loadingDetail = true;
		try {
			const detail = await getStatute(state.scenario.id, statuteId);
			detail._type = 'statute';
			collectAuthority({
				id: detail.id,
				type: 'statute',
				name: detail.title,
				title: detail.title,
			});
			setCurrentDetail(detail);
		} catch (err) {
			console.error('Failed to load statute:', err);
		} finally {
			loadingDetail = false;
		}
	}

	function handleBuildArgument() {
		goToArgument();
		goto(`/argument/${state.scenario.id}`);
	}
</script>

<GameGuard requiredPhases={['research', 'argument']}>
{#if state.scenario}
	<div class="research-workspace">
		<div class="left-panel">
			<div class="panel-tabs">
				<button
					class="tab-btn"
					class:active={!showCollected}
					onclick={() => showCollected = false}
				>
					Search
				</button>
				<button
					class="tab-btn"
					class:active={showCollected}
					onclick={() => showCollected = true}
				>
					Collected ({state.collectedAuthorities.length})
				</button>
			</div>

			{#if !showCollected}
				<form class="search-form" onsubmit={handleSearch}>
					<input
						type="text"
						bind:value={query}
						placeholder="Search cases and statutes..."
						disabled={!state.canSearch || searching}
					/>
					<button
						class="btn-primary"
						type="submit"
						disabled={!state.canSearch || searching || !query.trim()}
					>
						{searching ? '...' : 'Search'}
					</button>
					<span class="search-cost">{state.scenario.costs.search} hrs</span>
				</form>

				{#if state.hoursExpired}
					<div class="hours-expired-notice">
						<p>Time's up! Build your argument with what you've found.</p>
						<button class="btn-primary" onclick={handleBuildArgument}>
							Build Argument
						</button>
					</div>
				{/if}

				{#if hasResults}
					<div class="results">
						{#if searchResults.statutes.length > 0}
							<h4>Statutes</h4>
							{#each searchResults.statutes as statute}
								<button
									class="case-card statute-card"
									onclick={() => handleReadStatute(statute.id)}
									disabled={!state.canReadStatute || loadingDetail}
								>
									<div class="case-name">{statute.title}</div>
									<div class="case-tags">
										{#each statute.tags.slice(0, 3) as tag}
											<span class="tag">{tag}</span>
										{/each}
									</div>
								</button>
							{/each}
						{/if}

						{#if searchResults.cases.length > 0}
							<h4>Cases</h4>
							{#each searchResults.cases as c}
								<CaseCard
									caseData={c}
									active={state.currentDetail?.id === c.id}
									onclick={() => handleReadCase(c.id)}
								/>
							{/each}
						{/if}
					</div>
				{:else if state.searchHistory.length > 0}
					<p class="no-results">No results. Try different search terms.</p>
				{/if}
			{:else}
				<div class="collected-list">
					{#if state.collectedAuthorities.length === 0}
						<p class="no-results">No authorities collected yet. Search and read cases to build your collection.</p>
					{:else}
						{#each state.collectedAuthorities as auth}
							<button
								class="case-card collected-card"
								onclick={() => {
									// Re-read from cache (currentDetail) if it matches
									// Otherwise just highlight it
								}}
							>
								<div class="case-name">{auth.name}</div>
								<div class="case-meta">
									{#if auth.citation}
										<span>{auth.citation}</span>
									{/if}
									{#if auth.court}
										<span>{auth.court}</span>
									{/if}
								</div>
								<span class="tag">{auth.type}</span>
							</button>
						{/each}
					{/if}
				</div>
			{/if}

			<div class="panel-footer">
				<button class="btn-primary" onclick={handleBuildArgument}>
					Build Argument ({state.collectedAuthorities.length} authorities)
				</button>
			</div>
		</div>

		<div class="right-panel">
			{#if state.currentDetail}
				<div class="detail-scroll">
					{#if state.currentDetail._type === 'case'}
						<CaseDetail caseData={state.currentDetail} scenarioId={state.scenario.id} />
					{:else}
						<StatuteDetail statuteData={state.currentDetail} scenarioId={state.scenario.id} />
					{/if}
				</div>
			{:else}
				<div class="empty-detail">
					<p>Search for cases and statutes, then click one to read it here.</p>
					<p class="hint">Tip: Following citations is cheaper than searching ({state.scenario.costs.follow_citation} hrs vs {state.scenario.costs.search} hrs).</p>
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="container">
		<p>No scenario loaded. <a href="/">Return to home</a>.</p>
	</div>
{/if}
</GameGuard>

<style>
	.research-workspace {
		display: grid;
		grid-template-columns: 380px 1fr;
		height: calc(100vh - 52px);
		overflow: hidden;
	}

	.left-panel {
		border-right: 1px solid var(--color-text-dim);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.panel-tabs {
		display: flex;
		border-bottom: 1px solid var(--color-text-dim);
	}

	.tab-btn {
		flex: 1;
		background: var(--color-surface);
		color: var(--color-text-muted);
		border: none;
		border-radius: 0;
		padding: 0.6rem;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.tab-btn.active {
		color: var(--color-accent);
		border-bottom: 2px solid var(--color-accent);
	}

	.search-form {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.75rem;
		border-bottom: 1px solid var(--color-text-dim);
	}

	.search-form input {
		flex: 1;
		min-width: 0;
	}

	.search-cost {
		font-family: var(--font-ui);
		font-size: 0.75rem;
		color: var(--color-text-dim);
		white-space: nowrap;
	}

	.results, .collected-list {
		flex: 1;
		overflow-y: auto;
		padding: 0.75rem;
	}

	.results h4 {
		font-family: var(--font-ui);
		font-size: 0.8rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.5rem;
		margin-top: 0.75rem;
	}

	.results h4:first-child {
		margin-top: 0;
	}

	.no-results {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		color: var(--color-text-dim);
		padding: 1.5rem;
		text-align: center;
	}

	.hours-expired-notice {
		background: rgba(244, 67, 54, 0.1);
		border: 1px solid var(--color-danger);
		margin: 0.75rem;
		padding: 1rem;
		border-radius: var(--radius);
		text-align: center;
	}

	.hours-expired-notice p {
		font-family: var(--font-ui);
		color: var(--color-danger);
		margin-bottom: 0.75rem;
	}

	.statute-card {
		display: block;
		width: 100%;
		text-align: left;
		background: var(--color-surface);
		border: 1px solid var(--color-text-dim);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		margin-bottom: 0.5rem;
		cursor: pointer;
	}

	.statute-card:hover {
		border-color: var(--color-accent);
		background: var(--color-surface-light);
	}

	.case-name {
		font-family: var(--font-ui);
		font-weight: 600;
		font-size: 0.95rem;
		margin-bottom: 0.3rem;
	}

	.case-meta {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-bottom: 0.3rem;
	}

	.case-meta span {
		margin-right: 0.75rem;
	}

	.collected-card {
		display: block;
		width: 100%;
		text-align: left;
		background: var(--color-surface);
		border: 1px solid var(--color-text-dim);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		margin-bottom: 0.5rem;
		cursor: default;
	}

	.panel-footer {
		padding: 0.75rem;
		border-top: 1px solid var(--color-text-dim);
		background: var(--color-surface);
	}

	.panel-footer button {
		width: 100%;
	}

	.right-panel {
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.detail-scroll {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem 2rem;
	}

	.empty-detail {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		padding: 2rem;
	}

	.empty-detail p {
		font-family: var(--font-ui);
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.hint {
		font-size: 0.85rem;
		color: var(--color-text-dim);
	}
</style>
