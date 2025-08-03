<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher, onMount, getContext } from 'svelte';
	import { getLMStudioConfig, setLMStudioConfig } from '$lib/apis/configs';
	import { config } from '$lib/stores';
	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	export let saveHandler: Function;

	// LM Studio Integration Settings
	let lmStudioEnabled = false;
	let lmStudioUrl = 'http://localhost:1234';
	let lmStudioApiKey = '';
	let autoModelRefresh = true;
	let enableStreaming = true;
	let maxTokens = 4096;
	let temperature = 0.7;
	let topP = 0.9;
	let topK = 40;
	let repeatPenalty = 1.1;
	let connectionTimeout = 30;
	let enableCors = true;
	let enableLogging = false;
	let modelLoadTimeout = 60;

	let lmStudioConfig = null;

	const submitHandler = async () => {
		const lmStudioConfig = {
			enabled: lmStudioEnabled,
			url: lmStudioUrl,
			api_key: lmStudioApiKey,
			auto_model_refresh: autoModelRefresh,
			enable_streaming: enableStreaming,
			max_tokens: maxTokens,
			temperature: temperature,
			top_p: topP,
			top_k: topK,
			repeat_penalty: repeatPenalty,
			connection_timeout: connectionTimeout,
			enable_cors: enableCors,
			enable_logging: enableLogging,
			model_load_timeout: modelLoadTimeout
		};

		const res = await setLMStudioConfig(localStorage.token, lmStudioConfig);
	};

	onMount(async () => {
		const res = await getLMStudioConfig(localStorage.token);
		if (res) {
			lmStudioConfig = res;
			// Load values from config
			lmStudioEnabled = lmStudioConfig.enabled ?? false;
			lmStudioUrl = lmStudioConfig.url ?? 'http://localhost:1234';
			lmStudioApiKey = lmStudioConfig.api_key ?? '';
			autoModelRefresh = lmStudioConfig.auto_model_refresh ?? true;
			enableStreaming = lmStudioConfig.enable_streaming ?? true;
			maxTokens = lmStudioConfig.max_tokens ?? 4096;
			temperature = lmStudioConfig.temperature ?? 0.7;
			topP = lmStudioConfig.top_p ?? 0.9;
			topK = lmStudioConfig.top_k ?? 40;
			repeatPenalty = lmStudioConfig.repeat_penalty ?? 1.1;
			connectionTimeout = lmStudioConfig.connection_timeout ?? 30;
			enableCors = lmStudioConfig.enable_cors ?? true;
			enableLogging = lmStudioConfig.enable_logging ?? false;
			modelLoadTimeout = lmStudioConfig.model_load_timeout ?? 60;
		}
	});
</script>

<div class="flex flex-col h-full justify-between space-y-3 text-sm">
	<div class="space-y-3">
		<div>
			<div class="mb-2 text-sm font-medium">{$i18n.t('LM Studio Integration')}</div>
			<div class="text-xs text-gray-400 mb-3">
				{$i18n.t('Configure LM Studio connection for local language model inference')}
			</div>
		</div>

		<!-- Enable LM Studio -->
		<div class="flex w-full justify-between">
			<div class="flex items-center space-x-2">
				<span>{$i18n.t('Enable LM Studio')}</span>
				<Tooltip content={$i18n.t('Enable connection to LM Studio server for local AI inference')}>
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
							d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
						/>
					</svg>
				</Tooltip>
			</div>
			<Switch bind:state={lmStudioEnabled} />
		</div>

		<!-- LM Studio Configuration -->
		{#if lmStudioEnabled}
			<div class="flex flex-col space-y-2">
				<div class="flex items-center space-x-2">
					<span class="text-sm font-medium">{$i18n.t('LM Studio URL')}</span>
					<Tooltip content={$i18n.t('LM Studio server URL (default: http://localhost:1234)')}>
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
								d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
							/>
						</svg>
					</Tooltip>
				</div>
				<input
					class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
					type="url"
					placeholder="http://localhost:1234"
					bind:value={lmStudioUrl}
				/>
			</div>

			<div class="flex flex-col space-y-2">
				<div class="flex items-center space-x-2">
					<span class="text-sm font-medium">{$i18n.t('API Key')}</span>
					<Tooltip content={$i18n.t('Optional API key for LM Studio authentication')}>
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
								d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
							/>
						</svg>
					</Tooltip>
				</div>
				<input
					class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
					type="password"
					placeholder="Optional API key"
					bind:value={lmStudioApiKey}
				/>
			</div>

			<!-- Model & Inference Settings -->
			<div class="space-y-3">
				<div class="text-sm font-medium">{$i18n.t('Model & Inference Settings')}</div>

				<div class="flex w-full justify-between">
					<div class="flex items-center space-x-2">
						<span>{$i18n.t('Auto Model Refresh')}</span>
						<Tooltip content={$i18n.t('Automatically refresh available models from LM Studio')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<Switch bind:state={autoModelRefresh} />
				</div>

				<div class="flex w-full justify-between">
					<div class="flex items-center space-x-2">
						<span>{$i18n.t('Enable Streaming')}</span>
						<Tooltip content={$i18n.t('Enable streaming responses from LM Studio')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<Switch bind:state={enableStreaming} />
				</div>

				<div class="flex w-full justify-between">
					<div class="flex items-center space-x-2">
						<span>{$i18n.t('Enable CORS')}</span>
						<Tooltip content={$i18n.t('Enable Cross-Origin Resource Sharing for web requests')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<Switch bind:state={enableCors} />
				</div>

				<div class="flex w-full justify-between">
					<div class="flex items-center space-x-2">
						<span>{$i18n.t('Enable Logging')}</span>
						<Tooltip content={$i18n.t('Enable detailed logging for LM Studio requests and responses')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<Switch bind:state={enableLogging} />
				</div>
			</div>

			<!-- Timeout Settings -->
			<div class="space-y-3">
				<div class="text-sm font-medium">{$i18n.t('Timeout Settings')}</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Connection Timeout (seconds)')}</span>
						<Tooltip content={$i18n.t('Timeout for connecting to LM Studio server')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="5"
						max="300"
						bind:value={connectionTimeout}
					/>
				</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Model Load Timeout (seconds)')}</span>
						<Tooltip content={$i18n.t('Timeout for loading models in LM Studio')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="10"
						max="600"
						bind:value={modelLoadTimeout}
					/>
				</div>
			</div>

			<!-- Advanced Model Parameters -->
			<div class="space-y-3">
				<div class="text-sm font-medium">{$i18n.t('Model Parameters')}</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Max Tokens')}</span>
						<Tooltip content={$i18n.t('Maximum number of tokens to generate')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="1"
						max="32768"
						bind:value={maxTokens}
					/>
				</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Temperature')}</span>
						<Tooltip content={$i18n.t('Controls randomness in responses (0.0 = deterministic, 2.0 = very random)')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="0"
						max="2"
						step="0.1"
						bind:value={temperature}
					/>
				</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Top P')}</span>
						<Tooltip content={$i18n.t('Nucleus sampling parameter (0.1 = very focused, 1.0 = full vocabulary)')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="0.1"
						max="1.0"
						step="0.05"
						bind:value={topP}
					/>
				</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Top K')}</span>
						<Tooltip content={$i18n.t('Limits vocabulary to top K most likely tokens')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="1"
						max="100"
						bind:value={topK}
					/>
				</div>

				<div class="flex flex-col space-y-2">
					<div class="flex items-center space-x-2">
						<span class="text-sm">{$i18n.t('Repeat Penalty')}</span>
						<Tooltip content={$i18n.t('Penalty for repeating tokens (1.0 = no penalty, >1.0 = penalize repetition)')}>
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
									d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
								/>
							</svg>
						</Tooltip>
					</div>
					<input
						class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
						type="number"
						min="1.0"
						max="2.0"
						step="0.1"
						bind:value={repeatPenalty}
					/>
				</div>
			</div>
		{/if}
	</div>

	<div class="flex justify-end pt-3">
		<button
			class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
			on:click={saveSettings}
		>
			{$i18n.t('Save Settings')}
		</button>
	</div>
</div>