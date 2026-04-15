<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { onMount, getContext } from 'svelte';
	import { ARKIVE_NAME, config, user } from '$lib/stores';
	import { goto } from '$app/navigation';

	const i18n = getContext<Writable<i18nType>>('i18n');

	let loaded = false;

	onMount(async () => {
		if (
			!(
				($config?.features?.enable_notes ?? false) &&
				($user?.role === 'admin' || ($user?.permissions?.features?.notes ?? true))
			)
		) {
			// If the feature is not enabled, redirect to the home page
			goto('/');
		}

		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Notes')} • {$ARKIVE_NAME}
	</title>
</svelte:head>

{#if loaded}
	<slot />
{/if}
