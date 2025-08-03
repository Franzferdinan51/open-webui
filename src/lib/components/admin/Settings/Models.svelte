<script lang="ts">
	import { marked } from 'marked';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { onMount, getContext, tick } from 'svelte';
	const i18n = getContext('i18n');

	import { WEBUI_NAME, config, mobile, models as _models, settings, user } from '$lib/stores';
	import {
		createNewModel,
		deleteAllModels,
		getBaseModels,
		toggleModelById,
		updateModelById
	} from '$lib/apis/models';
	import { copyToClipboard } from '$lib/utils';
	import { page } from '$app/stores';

	import { getModels } from '$lib/apis';
	import { getLMStudioModels, loadLMStudioModel, unloadLMStudioModel } from '$lib/apis/lmstudio';
	import Search from '$lib/components/icons/Search.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';

	import ModelEditor from '$lib/components/workspace/Models/ModelEditor.svelte';
	import { toast } from 'svelte-sonner';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import Cog6 from '$lib/components/icons/Cog6.svelte';
	import ConfigureModelsModal from './Models/ConfigureModelsModal.svelte';
	import Wrench from '$lib/components/icons/Wrench.svelte';
	import ArrowDownTray from '$lib/components/icons/ArrowDownTray.svelte';
	import ManageModelsModal from './Models/ManageModelsModal.svelte';
	import ModelMenu from '$lib/components/admin/Settings/Models/ModelMenu.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import Eye from '$lib/components/icons/Eye.svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';

	let shiftKey = false;

	let importFiles;
	let modelsImportInputElement: HTMLInputElement;

	let models = null;
	let lmStudioModels = null;
	let allModels = null;

	let workspaceModels = null;
	let baseModels = null;

	let filteredModels = [];
	let selectedModelId = null;

	let showConfigModal = false;
	let showManageModal = false;

	$: if (allModels) {
		filteredModels = allModels
			.filter((m) => {
				// Filter by search value
				const matchesSearch = searchValue === '' || m.name.toLowerCase().includes(searchValue.toLowerCase());
				
				// Filter by provider
				const matchesProvider = selectedProvider === 'all' || 
					(selectedProvider === 'ollama' && m.provider !== 'lmstudio') ||
					(selectedProvider === 'lmstudio' && m.provider === 'lmstudio');
				
				return matchesSearch && matchesProvider;
			})
			.sort((a, b) => {
				// Sort by provider first, then alphabetically
				if (a.provider !== b.provider) {
					return a.provider.localeCompare(b.provider);
				}
				return a.name.localeCompare(b.name);
			});
	}

	let searchValue = '';
	let selectedProvider = 'all'; // 'all', 'ollama', 'lmstudio'

	const downloadModels = async (models) => {
		let blob = new Blob([JSON.stringify(models)], {
			type: 'application/json'
		});
		saveAs(blob, `models-export-${Date.now()}.json`);
	};

	const init = async () => {
		models = null;
		lmStudioModels = null;
		allModels = null;

		try {
			// Load Ollama models
			workspaceModels = await getBaseModels(localStorage.token);
			baseModels = await getModels(localStorage.token, null, true);

			models = baseModels.map((m) => {
				const workspaceModel = workspaceModels.find((wm) => wm.id === m.id);

				if (workspaceModel) {
					return {
						...m,
						...workspaceModel,
						provider: 'ollama'
					};
				} else {
					return {
						...m,
						id: m.id,
						name: m.name,
						is_active: true,
						provider: 'ollama'
					};
				}
			});

			// Load LM Studio models
			try {
				lmStudioModels = await getLMStudioModels(localStorage.token);
				if (lmStudioModels) {
					lmStudioModels = lmStudioModels.map((m) => ({
						...m,
						is_active: m.loaded ?? true,
						provider: 'lmstudio'
					}));
				}
			} catch (error) {
				console.warn('Failed to load LM Studio models:', error);
				lmStudioModels = [];
			}

			// Combine all models
			allModels = [...(models || []), ...(lmStudioModels || [])];
		} catch (error) {
			console.error('Error loading models:', error);
			allModels = [];
		}
	};

	const upsertModelHandler = async (model) => {
		model.base_model_id = null;

		if (workspaceModels.find((m) => m.id === model.id)) {
			const res = await updateModelById(localStorage.token, model.id, model).catch((error) => {
				return null;
			});

			if (res) {
				toast.success($i18n.t('Model updated successfully'));
			}
		} else {
			const res = await createNewModel(localStorage.token, {
				meta: {},
				id: model.id,
				name: model.name,
				base_model_id: null,
				params: {},
				access_control: {},
				...model
			}).catch((error) => {
				return null;
			});

			if (res) {
				toast.success($i18n.t('Model updated successfully'));
			}
		}
		await init();

		_models.set(
			await getModels(
				localStorage.token,
				$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
			)
		);
	};

	const toggleLMStudioModelHandler = async (model) => {
		try {
			if (model.is_active) {
				// Unload the model
				await unloadLMStudioModel(localStorage.token, model.id);
				toast.success($i18n.t('Model unloaded successfully'));
			} else {
				// Load the model
				await loadLMStudioModel(localStorage.token, model.id);
				toast.success($i18n.t('Model loaded successfully'));
			}
			
			// Refresh the models list
			await init();
		} catch (error) {
			console.error('Error toggling LM Studio model:', error);
			toast.error($i18n.t('Failed to toggle model'));
			
			// Revert the state
			model.is_active = !model.is_active;
		}
	};

	const toggleModelHandler = async (model) => {
		if (!Object.keys(model).includes('base_model_id')) {
			await createNewModel(localStorage.token, {
				id: model.id,
				name: model.name,
				base_model_id: null,
				meta: {},
				params: {},
				access_control: {},
				is_active: model.is_active
			}).catch((error) => {
				return null;
			});
		} else {
			await toggleModelById(localStorage.token, model.id);
		}

		// await init();
		_models.set(
			await getModels(
				localStorage.token,
				$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
			)
		);
	};

	const hideModelHandler = async (model) => {
		model.meta = {
			...model.meta,
			hidden: !(model?.meta?.hidden ?? false)
		};

		console.debug(model);

		toast.success(
			model.meta.hidden
				? $i18n.t(`Model {{name}} is now hidden`, {
						name: model.id
					})
				: $i18n.t(`Model {{name}} is now visible`, {
						name: model.id
					})
		);

		upsertModelHandler(model);
	};

	const copyLinkHandler = async (model) => {
		const baseUrl = window.location.origin;
		const res = await copyToClipboard(`${baseUrl}/?model=${encodeURIComponent(model.id)}`);

		if (res) {
			toast.success($i18n.t('Copied link to clipboard'));
		} else {
			toast.error($i18n.t('Failed to copy link'));
		}
	};

	const exportModelHandler = async (model) => {
		let blob = new Blob([JSON.stringify([model])], {
			type: 'application/json'
		});
		saveAs(blob, `${model.id}-${Date.now()}.json`);
	};

	onMount(async () => {
		await init();
		const id = $page.url.searchParams.get('id');

		if (id) {
			selectedModelId = id;
		}

		const onKeyDown = (event) => {
			if (event.key === 'Shift') {
				shiftKey = true;
			}
		};

		const onKeyUp = (event) => {
			if (event.key === 'Shift') {
				shiftKey = false;
			}
		};

		const onBlur = () => {
			shiftKey = false;
		};

		window.addEventListener('keydown', onKeyDown);
		window.addEventListener('keyup', onKeyUp);
		window.addEventListener('blur-sm', onBlur);

		return () => {
			window.removeEventListener('keydown', onKeyDown);
			window.removeEventListener('keyup', onKeyUp);
			window.removeEventListener('blur-sm', onBlur);
		};
	});
</script>

<ConfigureModelsModal bind:show={showConfigModal} initHandler={init} />
<ManageModelsModal bind:show={showManageModal} />

{#if models !== null}
	{#if selectedModelId === null}
		<div class="flex flex-col gap-1 mt-1.5 mb-2">
			<div class="flex justify-between items-center">
				<div class="flex items-center md:self-center text-xl font-medium px-0.5">
					{$i18n.t('Models')}
					<div class="flex self-center w-[1px] h-6 mx-2.5 bg-gray-50 dark:bg-gray-850" />
					<span class="text-lg font-medium text-gray-500 dark:text-gray-300"
						>{filteredModels.length}</span
					>
				</div>

				<div class="flex items-center gap-1.5">
					<Tooltip content={$i18n.t('Manage Models')}>
						<button
							class=" p-1 rounded-full flex gap-1 items-center"
							type="button"
							on:click={() => {
								showManageModal = true;
							}}
						>
							<ArrowDownTray />
						</button>
					</Tooltip>

					<Tooltip content={$i18n.t('Settings')}>
						<button
							class=" p-1 rounded-full flex gap-1 items-center"
							type="button"
							on:click={() => {
								showConfigModal = true;
							}}
						>
							<Cog6 />
						</button>
					</Tooltip>
				</div>
			</div>

			<div class=" flex flex-1 items-center w-full space-x-2">
				<div class="flex flex-1 items-center">
					<div class=" self-center ml-1 mr-3">
						<Search className="size-3.5" />
					</div>
					<input
						class=" w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={searchValue}
						placeholder={$i18n.t('Search Models')}
					/>
					{#if searchValue}
						<div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
							<button
								class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
								on:click={() => {
									searchValue = '';
								}}
							>
								<XMark className="size-3" strokeWidth="2" />
							</button>
						</div>
					{/if}
				</div>
				
				<!-- Provider Filter -->
				<div class="flex items-center">
					<select
						bind:value={selectedProvider}
						class="text-sm bg-transparent border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 outline-none"
					>
						<option value="all">{$i18n.t('All Providers')}</option>
						<option value="ollama">Ollama</option>
						<option value="lmstudio">LM Studio</option>
					</select>
				</div>
			</div>
		</div>

		<div class=" my-2 mb-5" id="model-list">
			{#if allModels && allModels.length > 0}
				{#each filteredModels as model, modelIdx (model.id)}
					<div
						class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-lg transition {model
							?.meta?.hidden
							? 'opacity-50 dark:opacity-50'
							: ''}"
						id="model-item-{model.id}"
					>
						<button
							class=" flex flex-1 text-left space-x-3.5 cursor-pointer w-full"
							type="button"
							on:click={() => {
								selectedModelId = model.id;
							}}
						>
							<div class=" self-center w-8">
								<div
									class=" rounded-full object-cover {(model?.is_active ?? true)
										? ''
										: 'opacity-50 dark:opacity-50'} "
								>
									<img
										src={model?.meta?.profile_image_url ?? `${WEBUI_BASE_URL}/static/favicon.png`}
										alt="modelfile profile"
										class=" rounded-full w-full h-auto object-cover"
									/>
								</div>
							</div>

							<div class=" flex-1 self-center {(model?.is_active ?? true) ? '' : 'text-gray-500'}">
								<Tooltip
									content={marked.parse(
										!!model?.meta?.description
											? model?.meta?.description
											: model?.ollama?.digest
												? `${model?.ollama?.digest} **(${model?.ollama?.modified_at})**`
												: model?.provider === 'lmstudio' && model?.path
													? `LM Studio: ${model.path}`
													: model.id
									)}
									className=" w-fit"
									placement="top-start"
								>
									<div class="flex items-center gap-2">
										<div class="font-semibold line-clamp-1">{model.name}</div>
										{#if model?.provider === 'lmstudio'}
											<span class="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1.5 py-0.5 rounded-full">LM Studio</span>
										{:else}
											<span class="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-1.5 py-0.5 rounded-full">Ollama</span>
										{/if}
									</div>
								</Tooltip>
								<div class=" text-xs overflow-hidden text-ellipsis line-clamp-1 text-gray-500">
									<span class=" line-clamp-1">
										{!!model?.meta?.description
											? model?.meta?.description
											: model?.provider === 'lmstudio'
												? model?.path || model.id
												: model?.ollama?.digest
													? `${model.id} (${model?.ollama?.digest})`
													: model.id}
									</span>
								</div>
							</div>
						</button>
						<div class="flex flex-row gap-0.5 items-center self-center">
							{#if shiftKey}
								<Tooltip content={model?.meta?.hidden ? $i18n.t('Show') : $i18n.t('Hide')}>
									<button
										class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
										type="button"
										on:click={() => {
											hideModelHandler(model);
										}}
									>
										{#if model?.meta?.hidden}
											<EyeSlash />
										{:else}
											<Eye />
										{/if}
									</button>
								</Tooltip>
							{:else}
								<button
									class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
									type="button"
									on:click={() => {
										selectedModelId = model.id;
									}}
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										stroke-width="1.5"
										stroke="currentColor"
										class="w-4 h-4"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
										/>
									</svg>
								</button>

								<ModelMenu
									user={$user}
									{model}
									exportHandler={() => {
										exportModelHandler(model);
									}}
									hideHandler={() => {
										hideModelHandler(model);
									}}
									copyLinkHandler={() => {
										copyLinkHandler(model);
									}}
									onClose={() => {}}
								>
									<button
										class="self-center w-fit text-sm p-1.5 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
										type="button"
									>
										<EllipsisHorizontal className="size-5" />
									</button>
								</ModelMenu>

								<div class="ml-1">
									<Tooltip
										content={model?.provider === 'lmstudio' 
											? ((model?.is_active ?? true) ? $i18n.t('Loaded') : $i18n.t('Unloaded'))
											: ((model?.is_active ?? true) ? $i18n.t('Enabled') : $i18n.t('Disabled'))}
									>
										<Switch
											bind:state={model.is_active}
											on:change={async () => {
												if (model?.provider === 'lmstudio') {
													await toggleLMStudioModelHandler(model);
												} else {
													await toggleModelHandler(model);
												}
											}}
										/>
									</Tooltip>
								</div>
							{/if}
						</div>
					</div>
				{/each}
			{:else}
				<div class="flex flex-col items-center justify-center w-full h-20">
					<div class="text-gray-500 dark:text-gray-400 text-xs">
						{$i18n.t('No models found')}
					</div>
				</div>
			{/if}
		</div>

		{#if $user?.role === 'admin'}
			<div class=" flex justify-end w-full mb-3">
				<div class="flex space-x-1">
					<input
						id="models-import-input"
						bind:this={modelsImportInputElement}
						bind:files={importFiles}
						type="file"
						accept=".json"
						hidden
						on:change={() => {
							console.log(importFiles);

							let reader = new FileReader();
							reader.onload = async (event) => {
								let savedModels = JSON.parse(event.target.result);
								console.log(savedModels);

								for (const model of savedModels) {
									if (Object.keys(model).includes('base_model_id')) {
										if (model.base_model_id === null) {
											upsertModelHandler(model);
										}
									} else {
										if (model?.info ?? false) {
											if (model.info.base_model_id === null) {
												upsertModelHandler(model.info);
											}
										}
									}
								}

								await _models.set(
									await getModels(
										localStorage.token,
										$config?.features?.enable_direct_connections &&
											($settings?.directConnections ?? null)
									)
								);
								init();
							};

							reader.readAsText(importFiles[0]);
						}}
					/>

					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
						on:click={() => {
							modelsImportInputElement.click();
						}}
					>
						<div class=" self-center mr-2 font-medium line-clamp-1">
							{$i18n.t('Import Presets')}
						</div>

						<div class=" self-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 16 16"
								fill="currentColor"
								class="w-3.5 h-3.5"
							>
								<path
									fill-rule="evenodd"
									d="M4 2a1.5 1.5 0 0 0-1.5 1.5v9A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V6.621a1.5 1.5 0 0 0-.44-1.06L9.94 2.439A1.5 1.5 0 0 0 8.878 2H4Zm4 9.5a.75.75 0 0 1-.75-.75V8.06l-.72.72a.75.75 0 0 1-1.06-1.06l2-2a.75.75 0 0 1 1.06 0l2 2a.75.75 0 1 1-1.06 1.06l-.72-.72v2.69a.75.75 0 0 1-.75.75Z"
									clip-rule="evenodd"
								/>
							</svg>
						</div>
					</button>

					<button
						class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
						on:click={async () => {
							downloadModels(models);
						}}
					>
						<div class=" self-center mr-2 font-medium line-clamp-1">
							{$i18n.t('Export Presets')} ({models.length})
						</div>

						<div class=" self-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 16 16"
								fill="currentColor"
								class="w-3.5 h-3.5"
							>
								<path
									fill-rule="evenodd"
									d="M4 2a1.5 1.5 0 0 0-1.5 1.5v9A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V6.621a1.5 1.5 0 0 0-.44-1.06L9.94 2.439A1.5 1.5 0 0 0 8.878 2H4Zm4 3.5a.75.75 0 0 1 .75.75v2.69l.72-.72a.75.75 0 1 1 1.06 1.06l-2 2a.75.75 0 0 1-1.06 0l-2-2a.75.75 0 0 1 1.06-1.06l.72.72V6.25A.75.75 0 0 1 8 5.5Z"
									clip-rule="evenodd"
								/>
							</svg>
						</div>
					</button>
				</div>
			</div>
		{/if}
	{:else}
		<ModelEditor
			edit
			model={models.find((m) => m.id === selectedModelId)}
			preset={false}
			onSubmit={(model) => {
				console.log(model);
				upsertModelHandler(model);
				selectedModelId = null;
			}}
			onBack={() => {
				selectedModelId = null;
			}}
		/>
	{/if}
{:else}
	<div class=" h-full w-full flex justify-center items-center">
		<Spinner className="size-5" />
	</div>
{/if}
