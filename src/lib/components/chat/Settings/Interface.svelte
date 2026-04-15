<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { getContext } from 'svelte';

	const i18n = getContext<Writable<i18nType>>('i18n');

	export const saveSettings: Function = () => {};
</script>

<div id="tab-interface" class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
	<div class="space-y-3 overflow-y-scroll max-h-[28rem] md:max-h-full">
		<div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
			{$i18n.t('Interface settings are configured by your administrator.')}
		</div>
	</div>
</div>
