<script lang="ts">
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { page } from '$app/stores';

	const i18n = getContext<Writable<i18nType>>('i18n');

	import { deleteGroupById, updateGroupById } from '$lib/apis/groups';
	import { DEFAULT_PERMISSIONS } from '$lib/constants/permissions';

	import Pencil from '$lib/components/icons/Pencil.svelte';
	import EditGroupModal from './EditGroupModal.svelte';

	type PermissionSet = typeof DEFAULT_PERMISSIONS;

	type Group = {
		id: string;
		name: string;
		description?: string;
		user_ids: Array<string | number>;
		member_count?: number;
		data?: Record<string, unknown>;
		permissions?: Partial<PermissionSet>;
	};

	export let group: Group = {
		id: '',
		name: 'Admins',
		user_ids: [1, 2, 3]
	};
	export let defaultPermissions: PermissionSet = DEFAULT_PERMISSIONS;

	export let setGroups: () => void | Promise<void> = () => {};

	let showEdit = false;

	const updateHandler = async (_group: {
		name: string;
		description: string;
		data: Record<string, unknown>;
		permissions: PermissionSet;
	}) => {
		const res = await updateGroupById(localStorage.token, group.id, _group).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Group updated successfully'));
			setGroups();
		}
	};

	const deleteHandler = async () => {
		const res = await deleteGroupById(localStorage.token, group.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Group deleted successfully'));
			setGroups();
		}
	};

	onMount(() => {
		const groupId = $page.url.searchParams.get('id');
		if (groupId && groupId === String(group.id)) {
			showEdit = true;
		}
	});
</script>

<EditGroupModal
	bind:show={showEdit}
	edit
	{group}
	{defaultPermissions}
	onSubmit={updateHandler}
	onDelete={deleteHandler}
/>

<button
	class="flex space-x-4 cursor-pointer text-left w-full px-3.5 py-2.5 dark:hover:bg-gray-850/50 hover:bg-gray-50 transition rounded-2xl"
	on:click={() => {
		showEdit = true;
	}}
>
	<div class="w-full">
		<div class="flex items-center justify-between">
			<div class="flex-1">
				<div class="flex items-center gap-2">
					<div class="text-sm font-medium line-clamp-1">{group.name}</div>
				</div>

				<div class="flex items-center gap-2 mt-0.5 line-clamp-1">
					<div class="text-xs text-gray-500 shrink-0">
						{$i18n.t('{{COUNT}} members', { COUNT: group?.member_count ?? 0 })}
					</div>

					{#if group?.description}
						<div class="text-xs text-gray-500 line-clamp-1">
							{group.description}
						</div>
					{/if}
				</div>
			</div>

			<div class="flex self-center ml-2">
				<Pencil className="size-3.5" />
			</div>
		</div>
	</div>
</button>
