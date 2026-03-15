<script>
	import { goto } from '$app/navigation';
	import { getState } from '$lib/game-state.svelte.js';

	let { requiredPhases = [], children } = $props();
	let state = $derived(getState());

	let allowed = $derived(
		state.scenario !== null && requiredPhases.includes(state.gamePhase)
	);

	$effect(() => {
		if (!allowed) {
			goto('/');
		}
	});
</script>

{#if allowed}
	{@render children()}
{/if}
