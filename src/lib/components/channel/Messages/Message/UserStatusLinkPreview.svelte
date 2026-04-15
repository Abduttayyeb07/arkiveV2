<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { getContext, onMount } from 'svelte';
	import { LinkPreview } from 'bits-ui';

	const i18n = getContext<Writable<i18nType>>('i18n');
	import { getUserInfoById } from '$lib/apis/users';

	import UserStatus from './UserStatus.svelte';

	type Side = 'top' | 'right' | 'bottom' | 'left';
	type Align = 'start' | 'center' | 'end';

	export let id: string | null = null;

	export let side: Side = 'top';
	export let align: Align = 'start';
	export let sideOffset = 6;

	let user = null;
	onMount(async () => {
		if (id) {
			user = await getUserInfoById(localStorage.token, id).catch((error) => {
				console.error('Error fetching user by ID:', error);
				return null;
			});
		}
	});
</script>

{#if user}
	<LinkPreview.Portal>
		<LinkPreview.Content
			class="w-[260px] rounded-2xl border border-gray-100  dark:border-gray-800 z-[9999] bg-white dark:bg-gray-850 dark:text-white shadow-lg transition"
			{side}
			{align}
			{sideOffset}
		>
			<UserStatus {user} />
		</LinkPreview.Content>
	</LinkPreview.Portal>
{/if}
