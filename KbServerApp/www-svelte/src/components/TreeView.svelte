<script>
	export let label
	export let tree
    export let selectFile

	let expandedStates = {}

	const toggleExpansion = (id) => {
		if (!expandedStates[id]) {
			expandedStates[id] = false
		}
		expandedStates[id] = !expandedStates[id]
	}
</script>

<ul>
	{#each Object.entries(tree) as [child_name, child_value], idx (child_name)}
		<li>
			{#if (typeof(child_value) == 'object')}
				<span on:click={() => toggleExpansion(child_name)}>
					<span class="arrow" class:arrowDown={expandedStates[child_name]}>&#x25b6</span>
					{child_name}
				</span>
				{#if expandedStates[child_name]}
					<svelte:self label={child_name} tree={child_value} {selectFile} />
				{/if}
			{:else}
				<span on:click={() => selectFile(child_name, child_value)}>
					<span class="no-arrow"/>
					{child_name}
				</span>
			{/if}
		</li>
	{/each}
</ul>


<style>
	ul {
		margin: 0;
		list-style: none;
		padding-left: 0.5em;
		user-select: none;
	}
	.no-arrow { padding-left: 1.0rem; }
	.arrow {
		cursor: pointer;
		display: inline-block;
	}
	.arrowDown { transform: rotate(90deg); }
</style>
