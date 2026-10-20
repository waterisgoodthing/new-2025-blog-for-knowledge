import { useCallback, useEffect, useState } from 'react'

import { adaptReviewItem } from '../../../adapters/ui-v2/from-backend'
import type { ReviewQueueModel } from '../../../contracts/ui-v2/review-queue'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { listDueReviewItems } from '../../../lib/api/review-items'

const LOADING: UiPageModel<ReviewQueueModel> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'backend',
}

export interface UseReviewQueueModelOptions {
	fetchQueue?: typeof listDueReviewItems
	autoFetch?: boolean
}

/**
 * Review queue data hook (T-U5-3, post-PR-08 contract re-audit): due items
 * adapted to display models + retry. Rating/re-answer submission stays on the
 * workspace page (PR-08); this hook is the read path for V2 previews.
 */
export function useReviewQueueModel(options: UseReviewQueueModelOptions = {}) {
	const { fetchQueue = listDueReviewItems, autoFetch = true } = options
	const [model, setModel] = useState<UiPageModel<ReviewQueueModel>>(LOADING)

	const refresh = useCallback(async () => {
		setModel(LOADING)
		try {
			const dtos = await fetchQueue()
			setModel({
				state: dtos.length === 0 ? 'empty' : 'ready',
				data: {
					items: dtos.map((dto) => adaptReviewItem(dto)),
					completedToday: null,
					source: 'backend',
				},
				error: null,
				source: 'backend',
			})
		} catch (error) {
			setModel({
				state: 'error',
				data: null,
				error: error instanceof Error ? error.message : '复习队列加载失败，请重试',
				source: 'backend',
			})
		}
	}, [fetchQueue])

	useEffect(() => {
		if (autoFetch) void refresh()
	}, [autoFetch, refresh])

	return { model, refresh }
}
