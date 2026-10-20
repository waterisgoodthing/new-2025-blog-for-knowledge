import type { DashboardModel } from '../../contracts/ui-v2/dashboard'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

function baseModel(overrides: Partial<DashboardModel>): DashboardModel {
	return {
		today: { dueCount: 3, overdueCount: 1, nextTask: null, source: 'mock' },
		review: { pendingCount: 5, dueTodayCount: 3, source: 'mock' },
		weaknesses: [
			{ name: '函数单调性', count: 4, subjects: ['数学'], source: 'mock' },
			{ name: '牛顿第二定律', count: 2, subjects: ['物理'], source: 'mock' },
		],
		recent: [
			{
				id: 'mock-q1',
				title: 'Mock：解析几何综合题',
				kind: 'question',
				updatedAt: '2026-09-15',
				source: 'mock',
			},
			{
				id: 'mock-m1',
				title: 'Mock：单调性错题复盘',
				kind: 'mistake',
				updatedAt: '2026-09-14',
				source: 'mock',
			},
		],
		trend: [
			{ label: '周一', value: 2, source: 'mock' },
			{ label: '周二', value: 3, source: 'mock' },
			{ label: '周三', value: null, source: 'mock' },
		],
		nextAction: {
			title: '处理到期复习',
			href: '/manage/review',
			reason: '3 项待处理',
			source: 'mock',
		},
		source: 'mock',
		...overrides,
	}
}

const emptyModel: DashboardModel = {
	today: { dueCount: 0, overdueCount: 0, nextTask: null, source: 'mock' },
	review: { pendingCount: 0, dueTodayCount: 0, source: 'mock' },
	weaknesses: [],
	recent: [],
	trend: [],
	nextAction: null,
	source: 'mock',
}

export const mockDashboardV2Normal: UiPageModel<DashboardModel> = {
	state: 'ready',
	data: baseModel({}),
	error: null,
	source: 'mock',
}

export const mockDashboardV2Empty: UiPageModel<DashboardModel> = {
	state: 'empty',
	data: emptyModel,
	error: null,
	source: 'mock',
}

export const mockDashboardV2Loading: UiPageModel<DashboardModel> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockDashboardV2Error: UiPageModel<DashboardModel> = {
	state: 'error',
	data: null,
	error: 'mock: 仪表盘加载失败，请重试',
	source: 'mock',
}

export const mockDashboardV2Partial: UiPageModel<DashboardModel> = {
	state: 'partial',
	data: baseModel({ weaknesses: [], trend: [], nextAction: null }),
	error: 'mock: 薄弱点与趋势暂不可用',
	source: 'mock',
}

export const mockDashboardV2NoData: UiPageModel<DashboardModel> = {
	state: 'ready',
	data: baseModel({
		today: { dueCount: null, overdueCount: null, nextTask: null, source: 'mock' },
		review: { pendingCount: null, dueTodayCount: null, source: 'mock' },
		weaknesses: [],
		trend: [],
		nextAction: null,
	}),
	error: null,
	source: 'mock',
}
