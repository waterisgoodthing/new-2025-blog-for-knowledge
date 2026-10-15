import type { ReviewQueueItem, ReviewQueueModel } from '../../../contracts/ui-v2/review-queue'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2DueBadge, Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

export function Uiv2ReviewTaskCard({ item }: { item: ReviewQueueItem }) {
	const overdue = item.task.status === 'overdue'
	return (
		<Uiv2Card title={item.task.title}>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2DueBadge overdue={overdue} />
				<Uiv2Badge text={item.task.subject} tone="note" />
				<Uiv2Badge
					text={item.task.priority === 'high' ? '优先' : item.task.priority === 'medium' ? '一般' : '低'}
					tone="neutral"
				/>
			</div>
			{item.questionExcerpt ? (
				<p className="text-[var(--uiv2-text-secondary)]">{item.questionExcerpt}</p>
			) : (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					暂无题干摘要
				</p>
			)}
			{item.hasReviewTarget ? (
				<a
					href="/manage/review"
					className="inline-flex min-h-[40px] items-center focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				>
					开始本次复习
				</a>
			) : (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					该复习项暂无可作答内容（等待 Week2 契约）
				</p>
			)}
		</Uiv2Card>
	)
}

export interface Uiv2ReviewSectionProps {
	model: UiPageModel<ReviewQueueModel>
	onRetry?: () => void
}

/**
 * Review queue section (U5): layout/queue/empty/error/partial on mocks.
 * No rating UI, no scheduling claims — Week2 owns the semantics.
 * Real integration: BLOCKED_BY_WEEK2.
 */
export function Uiv2ReviewSection({ model, onRetry }: Uiv2ReviewSectionProps) {
	return (
		<section aria-label="复习队列">
			<Uiv2SectionHeader title="复习" description="到期复习队列：一次一项，诚实记录" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载复习队列"
				emptyHint="复习队列是空的。确认错题后，到期的复习会出现在这里。"
				onRetry={onRetry}
			>
				{queue => (
					<ul className="grid gap-4 md:grid-cols-2">
						{queue.items.map(item => (
							<li key={item.task.id}>
								<Uiv2ReviewTaskCard item={item} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
