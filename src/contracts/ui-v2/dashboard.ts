// UI-facing contract: dashboard model (U2).
// UI Contract, NOT a backend DTO. Sections degrade independently: missing data
// => null + 'estimated' source; the UI must render honest empty states.

import type { MasterySource } from './mastery'
import type { ReviewTask } from './review-task'

export type DashboardSource = MasterySource

export interface DashboardToday {
	dueCount: number | null
	overdueCount: number | null
	nextTask: ReviewTask | null
	source: DashboardSource
}

export interface DashboardReview {
	pendingCount: number | null
	dueTodayCount: number | null
	source: DashboardSource
}

export interface DashboardWeaknessItem {
	name: string
	count: number | null
	subjects: string[]
	source: DashboardSource
}

export interface DashboardRecentItem {
	id: string
	title: string
	kind: 'question' | 'mistake' | 'review'
	updatedAt: string
	source: DashboardSource
}

export interface DashboardTrendPoint {
	label: string
	value: number | null
	source: DashboardSource
}

export interface DashboardNextAction {
	title: string
	href: string
	reason: string
	source: DashboardSource
}

export interface DashboardModel {
	today: DashboardToday
	review: DashboardReview
	weaknesses: DashboardWeaknessItem[]
	recent: DashboardRecentItem[]
	trend: DashboardTrendPoint[]
	nextAction: DashboardNextAction | null
	/** Where the whole model came from. Mocks must use 'mock'. */
	source: DashboardSource
}
