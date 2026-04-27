<script lang="ts">
	import type { i18n as i18nType } from 'i18next';
	import { toast } from 'svelte-sonner';
	import { getContext, onMount, onDestroy } from 'svelte';
	import type { Writable } from 'svelte/store';
	import dayjs from 'dayjs';

	import { searchFiles, deleteFileById } from '$lib/apis/files';
	import Modal from '$lib/components/common/Modal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Loader from '$lib/components/common/Loader.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import FileItemModal from '$lib/components/common/FileItemModal.svelte';
	import Checkbox from '$lib/components/common/Checkbox.svelte';

	const i18n: Writable<any> = getContext<Writable<i18nType>>('i18n');

	export let show = false;

	let files: any[] | null = null;
	let query = '';
	let orderBy = 'created_at';
	let direction = 'desc';

	let page = 0;
	let allFilesLoaded = false;
	let filesLoading = false;
	let searchDebounceTimer: ReturnType<typeof setTimeout>;

	let selectedFileId: string | null = null;
	let showDeleteConfirmDialog = false;
	let selectedFileIds: string[] = [];
	let showBulkDeleteConfirmDialog = false;

	let selectedFile: any = null;
	let showFileItemModal = false;

	let shiftKey = false;

	const PAGE_SIZE = 50;

	const formatFileSize = (bytes: number): string => {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
	};

	const setSortKey = (key: string) => {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			direction = 'asc';
		}
		searchHandler();
	};

	const searchHandler = async () => {
		if (!show) return;

		page = 0;
		files = null;
		allFilesLoaded = false;

		try {
			const pattern = query ? `*${query}*` : '*';
			const newFiles = await searchFiles(localStorage.token, pattern, 0, PAGE_SIZE);
			files = sortFiles(newFiles);
			allFilesLoaded = newFiles.length < PAGE_SIZE;
		} catch (error) {
			// Handle 404 or other errors - show empty state instead of spinner
			files = [];
			allFilesLoaded = true;
		}
	};

	const loadMoreFiles = async () => {
		if (filesLoading || allFilesLoaded) return;

		filesLoading = true;
		page += 1;

		try {
			const pattern = query ? `*${query}*` : '*';
			const newFiles = await searchFiles(localStorage.token, pattern, page * PAGE_SIZE, PAGE_SIZE);

			allFilesLoaded = newFiles.length < PAGE_SIZE;

			if (newFiles.length > 0) {
				files = sortFiles([...(files || []), ...newFiles]);
			}
		} catch (error) {
			// Handle errors silently for load more
			allFilesLoaded = true;
		}

		filesLoading = false;
	};

	const sortFiles = (fileList: any[]): any[] => {
		return fileList.sort((a, b) => {
			let aVal = a[orderBy] ?? 0;
			let bVal = b[orderBy] ?? 0;

			if (orderBy === 'filename') {
				aVal = a.filename?.toLowerCase() ?? '';
				bVal = b.filename?.toLowerCase() ?? '';
			}

			if (direction === 'asc') {
				return aVal > bVal ? 1 : -1;
			} else {
				return aVal < bVal ? 1 : -1;
			}
		});
	};

	const deleteHandler = async (fileId: string) => {
		try {
			await deleteFileById(localStorage.token, fileId);
			toast.success($i18n.t('File deleted successfully.'));
			// Remove from local array instead of re-fetching to allow rapid deletion
			files = files?.filter((f) => f.id !== fileId) ?? null;
			selectedFileIds = selectedFileIds.filter((id) => id !== fileId);
		} catch (error) {
			toast.error(`${error}`);
		}
	};

	const bulkDeleteHandler = async () => {
		const ids = [...selectedFileIds];
		let deletedCount = 0;

		for (const fileId of ids) {
			try {
				await deleteFileById(localStorage.token, fileId);
				deletedCount += 1;
			} catch (error) {
				toast.error(`${error}`);
			}
		}

		if (deletedCount > 0) {
			files = files?.filter((file) => !ids.includes(file.id)) ?? null;
			selectedFileIds = [];
			toast.success(
				$i18n.t('{{count}} files deleted successfully.', {
					count: deletedCount
				})
			);
		}
	};

	const toggleFileSelection = (fileId: string, selected: boolean) => {
		if (selected) {
			selectedFileIds = [...new Set([...selectedFileIds, fileId])];
		} else {
			selectedFileIds = selectedFileIds.filter((id) => id !== fileId);
		}
	};

	const visibleFileIds = () => (files ?? []).map((file) => file.id);

	const selectAllVisibleFiles = () => {
		selectedFileIds = [...new Set([...selectedFileIds, ...visibleFileIds()])];
	};

	const clearVisibleFileSelection = () => {
		const visibleIds = new Set(visibleFileIds());
		selectedFileIds = selectedFileIds.filter((id) => !visibleIds.has(id));
	};

	$: visibleSelectedCount = (files ?? []).filter((file) => selectedFileIds.includes(file.id)).length;
	$: allVisibleFilesSelected = (files?.length ?? 0) > 0 && visibleSelectedCount === files.length;

	const openFileViewer = (file: any) => {
		selectedFile = {
			id: file.id,
			name: file.filename,
			type: 'file',
			size: file.meta?.size,
			meta: file.meta
		};
		showFileItemModal = true;
	};

	// Debounce query changes
	$: if (show && query !== undefined) {
		clearTimeout(searchDebounceTimer);
		searchDebounceTimer = setTimeout(() => {
			searchHandler();
		}, 300);
	}

	onMount(() => {
		const onKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Shift') {
				shiftKey = true;
			}
		};

		const onKeyUp = (event: KeyboardEvent) => {
			if (event.key === 'Shift') {
				shiftKey = false;
			}
		};

		const onBlur = () => {
			shiftKey = false;
		};

		window.addEventListener('keydown', onKeyDown);
		window.addEventListener('keyup', onKeyUp);
		window.addEventListener('blur', onBlur);

		return () => {
			clearTimeout(searchDebounceTimer);
			window.removeEventListener('keydown', onKeyDown);
			window.removeEventListener('keyup', onKeyUp);
			window.removeEventListener('blur', onBlur);
		};
	});

	onDestroy(() => {
		clearTimeout(searchDebounceTimer);
	});
</script>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	on:confirm={async () => {
		if (selectedFileId) {
			await deleteHandler(selectedFileId);
			selectedFileId = null;
		}
	}}
/>

<ConfirmDialog
	bind:show={showBulkDeleteConfirmDialog}
	title={$i18n.t('Delete Selected Files')}
	message={$i18n.t('Are you sure you want to delete the selected files? This action cannot be undone.')}
	confirmLabel={$i18n.t('Delete')}
	on:confirm={bulkDeleteHandler}
/>

<FileItemModal bind:show={showFileItemModal} item={selectedFile} edit={false} />

<Modal size="xl" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-1">
			<div class="text-lg font-medium self-center">{$i18n.t('Files')}</div>
			<button
				class="self-center"
				type="button"
				aria-label={$i18n.t('Close')}
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						fill-rule="evenodd"
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
		</div>

		<div class="flex flex-col w-full px-5 pb-4 dark:text-gray-200">
			<!-- Search -->
			<div class="flex w-full space-x-2 mb-0.5">
				<div class="flex flex-1">
					<div class="self-center ml-1 mr-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 20 20"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								fill-rule="evenodd"
								d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<input
						class="w-full text-sm pr-4 py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={query}
						placeholder={$i18n.t('Search Files')}
						maxlength="500"
					/>

					{#if query}
						<div class="self-center pl-1.5 pr-1 translate-y-[0.5px] rounded-l-xl bg-transparent">
							<button
								class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
								type="button"
								aria-label={$i18n.t('Clear search')}
								on:click={() => {
									query = '';
								}}
							>
								<XMark className="size-3" strokeWidth="2" />
							</button>
						</div>
					{/if}
				</div>

				{#if selectedFileIds.length > 0}
					<div class="flex items-center gap-2 text-xs">
						<div class="text-gray-500 dark:text-gray-400 whitespace-nowrap">
							{$i18n.t('{{count}} selected', { count: selectedFileIds.length })}
						</div>
						<button
							class="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 transition"
							type="button"
							on:click={() => {
								showBulkDeleteConfirmDialog = true;
							}}
						>
							{$i18n.t('Delete Selected')}
						</button>
						<button
							class="px-2 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							type="button"
							on:click={() => {
								selectedFileIds = [];
							}}
						>
							{$i18n.t('Clear')}
						</button>
					</div>
				{/if}
			</div>

			<!-- Files List -->
			<div class="flex flex-col w-full">
				{#if files !== null}
					<div class="w-full">
						{#if files.length > 0}
							<div class="flex text-xs font-medium mb-1.5">
								<div class="px-1.5 py-1 w-8 flex justify-center">
									<Checkbox
										state={allVisibleFilesSelected ? 'checked' : 'unchecked'}
										on:change={(event) => {
											if (event.detail === 'checked') {
												selectAllVisibleFiles();
											} else {
												clearVisibleFileSelection();
											}
										}}
									/>
								</div>
								<button
									class="px-1.5 py-1 cursor-pointer select-none basis-3/5"
									type="button"
									on:click={() => setSortKey('filename')}
								>
									<div class="flex gap-1.5 items-center">
										{$i18n.t('Filename')}
										{#if orderBy === 'filename'}
											<span class="font-normal">
												{#if direction === 'asc'}
													<ChevronUp className="size-2" />
												{:else}
													<ChevronDown className="size-2" />
												{/if}
											</span>
										{:else}
											<span class="invisible">
												<ChevronUp className="size-2" />
											</span>
										{/if}
									</div>
								</button>
								<button
									class="px-1.5 py-1 cursor-pointer select-none hidden sm:flex sm:basis-2/5 justify-end"
									type="button"
									on:click={() => setSortKey('created_at')}
								>
									<div class="flex gap-1.5 items-center">
										{$i18n.t('Created at')}
										{#if orderBy === 'created_at'}
											<span class="font-normal">
												{#if direction === 'asc'}
													<ChevronUp className="size-2" />
												{:else}
													<ChevronDown className="size-2" />
												{/if}
											</span>
										{:else}
											<span class="invisible">
												<ChevronUp className="size-2" />
											</span>
										{/if}
									</div>
								</button>
							</div>
						{/if}

						<div class="text-left text-sm w-full mb-3 max-h-[32rem] overflow-y-scroll">
							{#if files.length === 0}
								<div
									class="text-xs text-gray-500 dark:text-gray-400 text-center px-5 min-h-20 w-full h-full flex justify-center items-center"
								>
									{$i18n.t('No files found')}
								</div>
							{/if}

							{#each files as file (file.id)}
								<div
									class="w-full flex justify-between items-center rounded-lg text-sm py-2 px-3 hover:bg-gray-50 dark:hover:bg-gray-850 cursor-pointer {selectedFileIds.includes(
										file.id
									)
										? 'bg-gray-50 dark:bg-gray-850'
										: ''}"
									role="button"
									tabindex="0"
									on:click={() => openFileViewer(file)}
									on:keydown={(event) => {
										if (event.key === 'Enter' || event.key === ' ') {
											event.preventDefault();
											openFileViewer(file);
										}
									}}
								>
									<div
										class="w-8 flex justify-center"
										role="presentation"
										on:click|preventDefault|stopPropagation
										on:keydown|stopPropagation
									>
										<Checkbox
											state={selectedFileIds.includes(file.id) ? 'checked' : 'unchecked'}
											on:change={(event) => {
												toggleFileSelection(file.id, event.detail === 'checked');
											}}
										/>
									</div>

									<div class="basis-3/5 min-w-0">
										<div class="text-ellipsis line-clamp-1">{file.filename}</div>
										<div class="text-xs text-gray-500">
											{formatFileSize(file.meta?.size ?? 0)}
										</div>
									</div>

									<div class="basis-2/5 flex items-center justify-end">
										<div class="hidden sm:flex text-gray-500 dark:text-gray-400 text-xs">
											{dayjs(file.created_at * 1000).format('MMM D, YYYY')}
										</div>

										<div class="flex justify-end pl-2.5 text-gray-600 dark:text-gray-300">
											<Tooltip content={shiftKey ? $i18n.t('Delete File') : $i18n.t('Delete File')}>
												<button
													class="self-center w-fit px-1 text-sm rounded-xl {shiftKey
														? 'text-red-500'
														: ''}"
													type="button"
													aria-label={$i18n.t('Delete File')}
													on:click|preventDefault|stopPropagation={() => {
														if (shiftKey) {
															deleteHandler(file.id);
														} else {
															selectedFileId = file.id;
															showDeleteConfirmDialog = true;
														}
													}}
												>
													<GarbageBin className="size-4" strokeWidth="1.5" />
												</button>
											</Tooltip>
										</div>
									</div>
								</div>
							{/each}

							{#if !allFilesLoaded}
								<Loader
									on:visible={() => {
										if (!filesLoading) {
											loadMoreFiles();
										}
									}}
								>
									<div
										class="w-full flex justify-center py-1 text-xs animate-pulse items-center gap-2"
									>
										<Spinner className="size-4" />
										<div>{$i18n.t('Loading...')}</div>
									</div>
								</Loader>
							{/if}
						</div>
					</div>
				{:else}
					<div class="w-full h-full flex justify-center items-center min-h-20">
						<Spinner className="size-5" />
					</div>
				{/if}
			</div>
		</div>
	</div>
</Modal>
