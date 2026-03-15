<script>
	import { goto } from '$app/navigation';
	import { submitArgument, getRebuttal } from '$lib/api.js';
	import {
		getState, assignToSlot, removeFromSlot,
		goToResearch, goToRebuttal, goToScore
	} from '$lib/game-state.svelte.js';
	import { getConfidence } from '$lib/scoring.js';
	import GameGuard from '$lib/components/GameGuard.svelte';

	let state = $derived(getState());

	let pickerSlotId = $state(null);
	let submitting = $state(false);
	let error = $state(null);

	let confidence = $derived(
		getConfidence(state.slotAssignments, state.scenario?.argument_slots)
	);

	function getAssignedAuthority(slotId) {
		const assignment = state.slotAssignments[slotId];
		if (!assignment) return null;
		return state.collectedAuthorities.find(a => a.id === assignment.authority_id);
	}

	function handlePickAuthority(slotId) {
		pickerSlotId = slotId;
	}

	function handleAssign(slotId, authority) {
		assignToSlot(slotId, authority.id, authority.type);
		pickerSlotId = null;
	}

	function handleRemove(slotId) {
		removeFromSlot(slotId);
	}

	function handleBackToResearch() {
		goToResearch();
		goto(`/research/${state.scenario.id}`);
	}

	async function handleSubmit() {
		if (submitting) return;
		submitting = true;
		error = null;

		const assignments = Object.entries(state.slotAssignments).map(
			([slot_id, { authority_id, authority_type }]) => ({
				slot_id,
				authority_id,
				authority_type,
			})
		);

		try {
			const result = await submitArgument(
				state.sessionId,
				assignments,
				state.billableHours
			);

			// Get rebuttal data
			const rebuttal = await getRebuttal(state.sessionId);
			goToRebuttal(rebuttal);
			// Store score for later
			goToScore(result);
			// Navigate to rebuttal first
			goto(`/rebuttal/${state.scenario.id}`);
		} catch (e) {
			error = e.message;
			submitting = false;
		}
	}

	function isAssignedElsewhere(authorityId, currentSlotId) {
		return Object.entries(state.slotAssignments).some(
			([slotId, a]) => slotId !== currentSlotId && a.authority_id === authorityId
		);
	}
</script>

<GameGuard requiredPhases={['argument', 'research']}>
{#if state.scenario}
	<div class="container argument-builder">
		<div class="builder-header">
			<h1>Build Your Argument</h1>
			<p>Assign your collected authorities to argument slots. Required slots must be filled to submit.</p>
		</div>

		<div class="confidence-meter">
			<span class="confidence-label">Argument Strength:</span>
			<span class="confidence-value confidence-{confidence.level}">
				{confidence.label}
			</span>
		</div>

		<div class="slots">
			{#each state.scenario.argument_slots as slot}
				{@const assigned = getAssignedAuthority(slot.slot_id)}
				<div class="slot-card" class:required={slot.required} class:filled={assigned}>
					<div class="slot-header">
						<h3>
							{slot.label}
							{#if slot.required}
								<span class="required-badge">Required</span>
							{/if}
						</h3>
						<p class="slot-description">{slot.description}</p>
					</div>

					{#if assigned}
						<div class="slot-assigned">
							<div class="assigned-name">{assigned.name}</div>
							{#if assigned.citation}
								<div class="assigned-meta">{assigned.citation}</div>
							{/if}
							<div class="slot-actions">
								<button class="btn-secondary btn-small" onclick={() => handlePickAuthority(slot.slot_id)}>
									Change
								</button>
								<button class="btn-secondary btn-small" onclick={() => handleRemove(slot.slot_id)}>
									Remove
								</button>
							</div>
						</div>
					{:else}
						<button
							class="slot-empty"
							onclick={() => handlePickAuthority(slot.slot_id)}
							disabled={state.collectedAuthorities.length === 0}
						>
							{state.collectedAuthorities.length === 0
								? 'No authorities collected'
								: 'Click to assign an authority'}
						</button>
					{/if}
				</div>
			{/each}
		</div>

		{#if pickerSlotId}
			<div class="picker-overlay" onclick={() => pickerSlotId = null} role="presentation">
				<div class="picker-panel" onclick={(e) => e.stopPropagation()} role="dialog">
					<h3>Select Authority for: {state.scenario.argument_slots.find(s => s.slot_id === pickerSlotId)?.label}</h3>
					<div class="picker-list">
						{#each state.collectedAuthorities as auth}
							{@const elsewhere = isAssignedElsewhere(auth.id, pickerSlotId)}
							<button
								class="picker-item"
								class:elsewhere
								onclick={() => handleAssign(pickerSlotId, auth)}
							>
								<div class="picker-name">{auth.name}</div>
								{#if auth.citation}
									<div class="picker-meta">{auth.citation}</div>
								{/if}
								<span class="tag">{auth.type}</span>
								{#if elsewhere}
									<span class="elsewhere-note">(assigned elsewhere)</span>
								{/if}
							</button>
						{/each}
					</div>
					<button class="btn-secondary" onclick={() => pickerSlotId = null}>Cancel</button>
				</div>
			</div>
		{/if}

		{#if error}
			<p class="error-msg">{error}</p>
		{/if}

		<div class="builder-actions">
			<button class="btn-secondary" onclick={handleBackToResearch}>
				Back to Research
			</button>
			<button
				class="btn-primary btn-large"
				disabled={!state.requiredSlotsFilled || submitting}
				onclick={handleSubmit}
			>
				{submitting ? 'Submitting...' : 'Submit Argument'}
			</button>
		</div>
	</div>
{:else}
	<div class="container">
		<p>No scenario loaded. <a href="/">Return to home</a>.</p>
	</div>
{/if}
</GameGuard>

<style>
	.argument-builder {
		max-width: 800px;
		margin: 0 auto;
		padding-top: 2rem;
		padding-bottom: 3rem;
	}

	.builder-header {
		margin-bottom: 1.5rem;
	}

	.builder-header h1 {
		font-size: 1.5rem;
		margin-bottom: 0.3rem;
	}

	.builder-header p {
		font-family: var(--font-ui);
		font-size: 0.9rem;
		color: var(--color-text-muted);
	}

	.confidence-meter {
		background: var(--color-surface);
		border-radius: var(--radius);
		padding: 0.75rem 1rem;
		margin-bottom: 1.5rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-family: var(--font-ui);
	}

	.confidence-label {
		color: var(--color-text-muted);
		font-size: 0.85rem;
	}

	.confidence-value {
		font-weight: 600;
		font-size: 0.9rem;
	}

	.confidence-none { color: var(--color-text-dim); }
	.confidence-weak { color: var(--color-danger); }
	.confidence-moderate { color: var(--color-warning); }
	.confidence-good { color: var(--color-link); }
	.confidence-strong { color: var(--color-success); }

	.slots {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.slot-card {
		background: var(--color-surface);
		border: 1px solid var(--color-text-dim);
		border-radius: var(--radius);
		padding: 1rem 1.25rem;
	}

	.slot-card.required {
		border-color: var(--color-accent);
	}

	.slot-card.filled {
		border-color: var(--color-success);
	}

	.slot-header h3 {
		font-size: 1rem;
		margin-bottom: 0.25rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.required-badge {
		font-size: 0.7rem;
		background: var(--color-accent);
		color: var(--color-bg);
		padding: 0.1rem 0.4rem;
		border-radius: 3px;
		font-weight: 700;
		text-transform: uppercase;
	}

	.slot-description {
		font-family: var(--font-ui);
		font-size: 0.85rem;
		color: var(--color-text-muted);
		margin-bottom: 0.75rem;
	}

	.slot-assigned {
		background: var(--color-surface-light);
		border-radius: var(--radius);
		padding: 0.75rem;
	}

	.assigned-name {
		font-family: var(--font-ui);
		font-weight: 600;
		margin-bottom: 0.2rem;
	}

	.assigned-meta {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-bottom: 0.5rem;
	}

	.slot-actions {
		display: flex;
		gap: 0.4rem;
	}

	.btn-small {
		font-size: 0.75rem;
		padding: 0.25rem 0.5rem;
	}

	.slot-empty {
		width: 100%;
		background: var(--color-bg);
		border: 1px dashed var(--color-text-dim);
		border-radius: var(--radius);
		padding: 0.75rem;
		color: var(--color-text-dim);
		font-family: var(--font-ui);
		font-size: 0.85rem;
		cursor: pointer;
	}

	.slot-empty:hover:not(:disabled) {
		border-color: var(--color-accent);
		color: var(--color-text-muted);
	}

	.picker-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.picker-panel {
		background: var(--color-surface);
		border-radius: var(--radius);
		padding: 1.5rem;
		max-width: 500px;
		width: 90%;
		max-height: 70vh;
		overflow-y: auto;
		box-shadow: var(--shadow);
	}

	.picker-panel h3 {
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.picker-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}

	.picker-item {
		text-align: left;
		background: var(--color-surface-light);
		border: 1px solid var(--color-text-dim);
		border-radius: var(--radius);
		padding: 0.75rem;
		cursor: pointer;
	}

	.picker-item:hover {
		border-color: var(--color-accent);
	}

	.picker-item.elsewhere {
		opacity: 0.6;
	}

	.picker-name {
		font-family: var(--font-ui);
		font-weight: 600;
		margin-bottom: 0.15rem;
	}

	.picker-meta {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin-bottom: 0.25rem;
	}

	.elsewhere-note {
		font-family: var(--font-ui);
		font-size: 0.75rem;
		color: var(--color-warning);
	}

	.error-msg {
		color: var(--color-danger);
		font-family: var(--font-ui);
		text-align: center;
		margin-bottom: 1rem;
	}

	.builder-actions {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.btn-large {
		padding: 0.75rem 2rem;
		font-size: 1.05rem;
	}
</style>
