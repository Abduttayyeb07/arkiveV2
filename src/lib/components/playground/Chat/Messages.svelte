<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { onMount, getContext } from 'svelte';
	import Message from './Message.svelte';

	const i18n = getContext<Writable<i18nType>>('i18n');

	export let messages = [];
</script>

<div class="py-3 space-y-3">
	{#each messages as message, idx}
		<Message
			{message}
			{idx}
			onDelete={() => {
				messages = messages.filter((message, messageIdx) => messageIdx !== idx);
			}}
		/>
	{/each}
</div>
