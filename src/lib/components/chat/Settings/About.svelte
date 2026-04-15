<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { ARKIVE_VERSION } from '$lib/constants';
	import { ARKIVE_NAME } from '$lib/stores';
	import { getContext } from 'svelte';

	const i18n = getContext<Writable<i18nType>>('i18n');
</script>

<div id="tab-about" class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
	<div class="space-y-3 overflow-y-scroll max-h-[28rem] md:max-h-full">
		<div>
			<div class="mb-2.5 text-sm font-medium">{$ARKIVE_NAME} {$i18n.t('Version')}</div>
			<div class="text-xs text-gray-500 dark:text-gray-400">v{ARKIVE_VERSION}</div>
		</div>

		<div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
			Copyright (c) {new Date().getFullYear()} {$ARKIVE_NAME} — Enterprise Intelligence Platform.
		</div>
	</div>
</div>
