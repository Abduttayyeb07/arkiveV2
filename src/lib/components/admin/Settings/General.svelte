<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { getBackendConfig } from '$lib/apis';
	import { getAdminConfig, updateAdminConfig } from '$lib/apis/auths';
	import { getGroups } from '$lib/apis/groups';
	import Switch from '$lib/components/common/Switch.svelte';
	import { config } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext<Writable<i18nType>>('i18n');

	export let saveHandler: Function;

	let adminConfig = null;
	let groups = [];

	const updateHandler = async () => {
		const res = await updateAdminConfig(localStorage.token, adminConfig);
		config.set(await getBackendConfig());

		if (res) {
			saveHandler();
		} else {
			toast.error($i18n.t('Failed to update settings'));
		}
	};

	onMount(async () => {
		adminConfig = await getAdminConfig(localStorage.token);
		groups = await getGroups(localStorage.token);
	});
</script>

<form
	class="flex flex-col h-full justify-between space-y-3 text-sm"
	on:submit|preventDefault={async () => {
		updateHandler();
	}}
>
	<div class="space-y-3 overflow-y-scroll scrollbar-hidden h-full">
		{#if adminConfig !== null}
			<div class="">
				<div class="mb-3.5">
					<div class=" mt-0.5 mb-2.5 text-base font-medium">{$i18n.t('General')}</div>

				</div>

				<div class="mb-3">
					<div class=" mt-0.5 mb-2.5 text-base font-medium">{$i18n.t('Authentication')}</div>

					<hr class=" border-gray-100/30 dark:border-gray-850/30 my-2" />

					<div class="  mb-2.5 flex w-full justify-between">
						<div class=" self-center text-xs font-medium">{$i18n.t('Default User Role')}</div>
						<div class="flex items-center relative">
							<select
								class="w-fit pr-8 rounded-sm px-2 text-xs bg-transparent outline-hidden text-right"
								bind:value={adminConfig.DEFAULT_USER_ROLE}
								placeholder={$i18n.t('Select a role')}
							>
								<option value="pending">{$i18n.t('pending')}</option>
								<option value="user">{$i18n.t('user')}</option>
								<option value="admin">{$i18n.t('admin')}</option>
							</select>
						</div>
					</div>

					<div class="  mb-2.5 flex w-full justify-between">
						<div class=" self-center text-xs font-medium">{$i18n.t('Default Group')}</div>
						<div class="flex items-center relative">
							<select
								class="w-fit pr-8 rounded-sm px-2 text-xs bg-transparent outline-hidden text-right"
								bind:value={adminConfig.DEFAULT_GROUP_ID}
								placeholder={$i18n.t('Select a group')}
							>
								<option value={''}>None</option>
								{#each groups as group}
									<option value={group.id}>{group.name}</option>
								{/each}
							</select>
						</div>
					</div>

					<div class=" mb-2.5 flex w-full justify-between pr-2">
						<div class=" self-center text-xs font-medium">{$i18n.t('Enable New Sign Ups')}</div>

						<Switch bind:state={adminConfig.ENABLE_SIGNUP} />
					</div>

					<div class="mb-2.5 flex w-full items-center justify-between pr-2">
						<div class=" self-center text-xs font-medium">
							{$i18n.t('Show Admin Details in Account Pending Overlay')}
						</div>

						<Switch bind:state={adminConfig.SHOW_ADMIN_DETAILS} />
					</div>

					{#if adminConfig.SHOW_ADMIN_DETAILS}
						<div class="mb-2.5 w-full justify-between">
							<div class="flex w-full justify-between">
								<div class=" self-center text-xs font-medium">{$i18n.t('Admin Contact Email')}</div>
							</div>

							<div class="flex mt-2 space-x-2">
								<input
									class="w-full rounded-lg py-2 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden"
									type="email"
									placeholder={$i18n.t('Leave empty to use first admin user')}
									bind:value={adminConfig.ADMIN_EMAIL}
								/>
							</div>
						</div>
					{/if}

					<div class="mb-2.5 flex w-full justify-between pr-2">
						<div class=" self-center text-xs font-medium">{$i18n.t('Enable API Keys')}</div>

						<Switch bind:state={adminConfig.ENABLE_API_KEYS} />
					</div>

					{#if adminConfig?.ENABLE_API_KEYS}
						<div class="mb-2.5 flex w-full justify-between pr-2">
							<div class=" self-center text-xs font-medium">
								{$i18n.t('API Key Endpoint Restrictions')}
							</div>

							<Switch bind:state={adminConfig.ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS} />
						</div>

						{#if adminConfig?.ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS}
							<div class=" flex w-full flex-col pr-2 mb-2.5">
								<div class=" text-xs font-medium">
									{$i18n.t('Allowed Endpoints')}
								</div>

								<input
									class="w-full mt-1 text-sm dark:text-gray-300 bg-transparent outline-hidden"
									type="text"
									placeholder={`e.g.) /api/v1/messages, /api/v1/channels`}
									bind:value={adminConfig.API_KEYS_ALLOWED_ENDPOINTS}
								/>

								<div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
									<span class=" text-gray-300 font-medium">
										{$i18n.t('To learn more about available endpoints, visit our documentation.')}
									</span>
								</div>
							</div>
						{/if}
					{/if}

					<div class=" mb-2.5 w-full justify-between">
						<div class="flex w-full justify-between">
							<div class=" self-center text-xs font-medium">{$i18n.t('JWT Expiration')}</div>
						</div>

						<div class="flex mt-2 space-x-2">
							<input
								class="w-full rounded-lg py-2 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden"
								type="text"
								placeholder={`e.g.) "30m","1h", "10d". `}
								bind:value={adminConfig.JWT_EXPIRES_IN}
							/>
						</div>

						<div class="mt-2 text-xs text-gray-400 dark:text-gray-500">
							{$i18n.t('Valid time units:')}
							<span class=" text-gray-300 font-medium"
								>{$i18n.t("'s', 'm', 'h', 'd', 'w' or '-1' for no expiration.")}</span
							>
						</div>

						{#if adminConfig.JWT_EXPIRES_IN === '-1'}
							<div class="mt-2 text-xs">
								<div
									class=" bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-3 py-2"
								>
									<div>
										<span class=" font-medium">{$i18n.t('Warning')}:</span>
										<span>{$i18n.t('No expiration can pose security risks.')}</span>
									</div>
								</div>
							</div>
						{/if}
					</div>

				</div>

				<div class="mb-3">
					<div class=" mt-0.5 mb-2.5 text-base font-medium">{$i18n.t('Features')}</div>

					<hr class=" border-gray-100/30 dark:border-gray-850/30 my-2" />

					<div class="mb-2.5 flex w-full items-center justify-between pr-2">
						<div class=" self-center text-xs font-medium">
							{$i18n.t('Folders')}
						</div>

						<Switch bind:state={adminConfig.ENABLE_FOLDERS} />
					</div>

				</div>
			</div>
		{/if}
	</div>

	<div class="flex justify-end pt-3 text-sm font-medium">
		<button
			class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			type="submit"
		>
			{$i18n.t('Save')}
		</button>
	</div>
</form>
