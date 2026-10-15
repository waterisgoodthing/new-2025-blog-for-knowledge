import type { AnalyticsModel } from '../../contracts/ui-v2/analytics'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

// Analytics mocks (U9). Includes a full-data variant and an all-null
// “数据积累中” variant. No algorithm output is fabricated.

const full: AnalyticsModel = {
	learningTrend: [
		{ label: '第 1 周', value: 4, source: 'mock' },
		{ label: '第 2 周', value: 7, source: 'mock' },
		{ label: '第 3 周', value: null, source: 'mock' },
	],
	reviewCompletion: { completed: 12, total: 15, source: 'mock' },
	mistakeTrend: [
		{ label: '第 1 周', newMistakes: 5, resolvedMistakes: 2, source: 'mock' },
		{ label: '第 2 周', newMistakes: 3, resolvedMistakes: 4, source: 'mock' },
	],
	weaknessDistribution: [
		{ name: '函数单调性', share: 0.4, count: 4, source: 'mock' },
		{ name: '牛顿第二定律', share: null, count: 2, source: 'mock' },
	],
	mastery: { value: null, confidence: 'low', source: 'mock' },
	source: 'mock',
}

const accumulating: AnalyticsModel = {
	learningTrend: [],
	reviewCompletion: { completed: null, total: null, source: 'mock' },
	mistakeTrend: [],
	weaknessDistribution: [],
	mastery: { value: null, confidence: 'low', source: 'mock' },
	source: 'mock',
}

export const mockAnalyticsNormal: UiPageModel<AnalyticsModel> = {
	state: 'ready',
	data: full,
	error: null,
	source: 'mock',
}

export const mockAnalyticsAccumulating: UiPageModel<AnalyticsModel> = {
	state: 'ready',
	data: accumulating,
	error: null,
	source: 'mock',
}

export const mockAnalyticsEmpty: UiPageModel<AnalyticsModel> = {
	state: 'empty',
	data: accumulating,
	error: null,
	source: 'mock',
}

export const mockAnalyticsLoading: UiPageModel<AnalyticsModel> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockAnalyticsError: UiPageModel<AnalyticsModel> = {
	state: 'error',
	data: null,
	error: 'mock: 学习分析加载失败，请重试',
	source: 'mock',
}
