import type { ReviewQueueModel } from '../../contracts/ui-v2/review-queue'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

// Review queue mocks (U5). source: 'mock'. No rating buttons, no scheduling
// claims: Week2 owns that semantics. dueAt values are illustrative only.

const normal: ReviewQueueModel = {
	items: [
		{
			task: {
				id: 'mock-rev-1',
				title: 'Mock：函数单调性错题',
				subject: '数学',
				priority: 'high',
				status: 'pending',
				source: 'mock',
			},
			questionExcerpt: '求 f(x)=x³-3x 的单调区间',
			hasReviewTarget: true,
			source: 'mock',
		},
		{
			task: {
				id: 'mock-rev-2',
				title: 'Mock：牛顿第二定律',
				subject: '物理',
				dueAt: '2026-09-14',
				priority: 'medium',
				status: 'overdue',
				source: 'mock',
			},
			questionExcerpt: null,
			hasReviewTarget: false,
			source: 'mock',
		},
	],
	completedToday: null,
	source: 'mock',
}

export const mockReviewV2Normal: UiPageModel<ReviewQueueModel> = {
	state: 'ready',
	data: normal,
	error: null,
	source: 'mock',
}

export const mockReviewV2Empty: UiPageModel<ReviewQueueModel> = {
	state: 'empty',
	data: { items: [], completedToday: null, source: 'mock' },
	error: null,
	source: 'mock',
}

export const mockReviewV2Loading: UiPageModel<ReviewQueueModel> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockReviewV2Error: UiPageModel<ReviewQueueModel> = {
	state: 'error',
	data: null,
	error: 'mock: 复习队列加载失败，请重试',
	source: 'mock',
}

export const mockReviewV2Partial: UiPageModel<ReviewQueueModel> = {
	state: 'partial',
	data: { ...normal, items: normal.items.slice(0, 1) },
	error: 'mock: 部分复习项暂不可用',
	source: 'mock',
}
