import type { ReactNode } from 'react'

import type { PageState, UiPageModel } from '../../contracts/ui-v2/ui-state'
import { Uiv2ErrorState } from './ErrorState'
import { Uiv2Skeleton } from './Skeleton'

export interface Uiv2PageStateViewProps<T> {
	model: UiPageModel<T>
	/** Accessible label for the loading status region. */
	loadingLabel?: string
	/** Rendered when state is 'empty'. */
	emptyHint: string
	/** Rendered when state is 'ready' or 'partial'. */
	children: (data: T, state: PageState) => ReactNode
	onRetry?: () => void
}

/**
 * Shared six-state renderer (U2): LOADING / EMPTY / ERROR / PARTIAL /
 * SUCCESS / RETRY. Error uses role="alert" with text (never raw secrets —
 * callers pass display-safe messages). Partial renders data plus a notice.
 */
export function Uiv2PageStateView<T>({
	model,
	loadingLabel = '正在加载内容',
	emptyHint,
	children,
	onRetry,
}: Uiv2PageStateViewProps<T>) {
	if (model.state === 'loading') {
		return (
			<div role="status" aria-label={loadingLabel}>
				<Uiv2Skeleton lines={3} />
				<p className="sr-only">{loadingLabel}</p>
			</div>
		)
	}
	if (model.state === 'error') {
		return <Uiv2ErrorState message={model.error ?? '加载失败，请重试'} onRetry={onRetry} />
	}
	if (model.state === 'empty' || model.data === null) {
		return <p className="text-[var(--uiv2-text-secondary)]">{emptyHint}</p>
	}
	return (
		<>
			{model.state === 'partial' ? (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					部分数据加载成功
					{model.error ? `：${model.error}` : ''}
				</p>
			) : null}
			{children(model.data, model.state)}
		</>
	)
}
