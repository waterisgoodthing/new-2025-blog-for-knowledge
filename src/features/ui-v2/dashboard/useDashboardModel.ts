import { useCallback, useEffect, useState } from 'react'

import { adaptDashboardSummary } from '../../../adapters/ui-v2/from-backend'
import type { DashboardModel } from '../../../contracts/ui-v2/dashboard'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { getDashboardSummary } from '../../../lib/api/dashboard'

const LOADING: UiPageModel<DashboardModel> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'backend',
}

export interface UseDashboardModelOptions {
	/** Override the fetcher in tests. Defaults to the real admin summary client. */
	fetchSummary?: typeof getDashboardSummary
	/** When false, the hook does not fetch on mount (preview/mock usage). */
	autoFetch?: boolean
}

/**
 * Dashboard data hook (U2): fetch → adapt → UiPageModel + retry.
 * Uses credentials-bearing apiFetch via the typed client; 401/403 surfaces as
 * error state (never silent). No raw DTO leaks: consumers only see DashboardModel.
 */
export function useDashboardModel(options: UseDashboardModelOptions = {}) {
	const { fetchSummary = getDashboardSummary, autoFetch = true } = options
	const [model, setModel] = useState<UiPageModel<DashboardModel>>(LOADING)

	const refresh = useCallback(async () => {
		setModel(LOADING)
		try {
			const dto = await fetchSummary()
			setModel({ state: 'ready', data: adaptDashboardSummary(dto), error: null, source: 'backend' })
		} catch (error) {
			setModel({
				state: 'error',
				data: null,
				error: error instanceof Error ? error.message : '仪表盘加载失败，请重试',
				source: 'backend',
			})
		}
	}, [fetchSummary])

	useEffect(() => {
		if (autoFetch) void refresh()
	}, [autoFetch, refresh])

	return { model, refresh }
}
