import type { StudyTask } from '../../contracts/ui-v2/study-task'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

// Today mocks (U3). There is no unified backend task endpoint (GAP-001), so
// every entry is source: 'mock' with an explicit provenance note. The UI must
// surface the note instead of presenting these as the real plan.

const mockTasks: StudyTask[] = [
	{
		id: 'mock-today-1',
		title: 'Mock：复习 3 项到期错题',
		kind: 'review',
		status: 'pending',
		priority: 'high',
		subject: '数学',
		href: '/manage/review',
		source: 'mock',
		provenanceNote: '示例任务，非真实学习计划（GAP-001）',
	},
	{
		id: 'mock-today-2',
		title: 'Mock：重做 2 道物理错题',
		kind: 'mistake_retry',
		status: 'overdue',
		priority: 'medium',
		subject: '物理',
		dueAt: '2026-09-14',
		href: '/manage/mistakes',
		source: 'mock',
		provenanceNote: '示例任务，非真实学习计划（GAP-001）',
	},
	{
		id: 'mock-today-3',
		title: 'Mock：新练 5 道解析几何',
		kind: 'new_practice',
		status: 'pending',
		priority: 'low',
		subject: '数学',
		href: '/manage/questions',
		source: 'mock',
		provenanceNote: '示例任务，非真实学习计划（GAP-001）',
	},
]

export const mockTodayNormal: UiPageModel<StudyTask[]> = {
	state: 'ready',
	data: mockTasks,
	error: null,
	source: 'mock',
}

export const mockTodayEmpty: UiPageModel<StudyTask[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockTodayLoading: UiPageModel<StudyTask[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockTodayError: UiPageModel<StudyTask[]> = {
	state: 'error',
	data: null,
	error: 'mock: 今日任务加载失败，请重试',
	source: 'mock',
}

export const mockTodayPartial: UiPageModel<StudyTask[]> = {
	state: 'partial',
	data: mockTasks.slice(0, 1),
	error: 'mock: 部分任务暂不可用',
	source: 'mock',
}

export const mockTodayOverdue: UiPageModel<StudyTask[]> = {
	state: 'ready',
	data: mockTasks.filter(t => t.status === 'overdue'),
	error: null,
	source: 'mock',
}
