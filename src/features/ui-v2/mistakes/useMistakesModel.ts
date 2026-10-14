import { useCallback, useEffect, useState } from 'react'

import { adaptMistake } from '../../../adapters/ui-v2/from-backend'
import type { MistakeCardModel } from '../../../contracts/ui-v2/mistake'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { listMistakes } from '../../../lib/api/mistakes'

const LOADING: UiPageModel<MistakeCardModel[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'backend',
}

export interface UseMistakesModelOptions {
	fetchMistakes?: typeof listMistakes
	autoFetch?: boolean
}

/**
 * Mistakes data hook (U4): listMistakes → adapt → UiPageModel + retry.
 * Read-only display path; no mutation in this track. Consumers only see
 * MistakeCardModel — never the raw DTO.
 */
export function useMistakesModel(options: UseMistakesModelOptions = {}) {
	const { fetchMistakes = listMistakes, autoFetch = true } = options
	const [model, setModel] = useState<UiPageModel<MistakeCardModel[]>>(LOADING)

	const refresh = useCallback(async () => {
		setModel(LOADING)
		try {
			const dtos = await fetchMistakes()
			setModel({
				state: dtos.length === 0 ? 'empty' : 'ready',
				data: dtos.map(adaptMistake),
				error: null,
				source: 'backend',
			})
		} catch (error) {
			setModel({
				state: 'error',
				data: null,
				error: error instanceof Error ? error.message : '错题加载失败，请重试',
				source: 'backend',
			})
		}
	}, [fetchMistakes])

	useEffect(() => {
		if (autoFetch) void refresh()
	}, [autoFetch, refresh])

	return { model, refresh }
}
