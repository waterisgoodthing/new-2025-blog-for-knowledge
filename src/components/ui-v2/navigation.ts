// UI V2 navigation config (U1).
// Read-only mapping: Current Route -> Proposed V2 Section. This file changes NO
// routing, guards, or ownership; it only describes grouping for V2 shell
// components. Statuses mirror docs/ui-v2/UI_V2_INFORMATION_ARCHITECTURE.md.

export type Uiv2NavStatus =
	| 'KEEP'
	| 'REFACTOR'
	| 'MIGRATE_LATER'
	| 'LEGACY'
	| 'NON_LEARNING'

export type Uiv2SectionId =
	| 'home'
	| 'learn'
	| 'knowledge'
	| 'analytics'
	| 'resources'
	| 'settings'

export interface Uiv2NavItem {
	/** Stable key for rendering + tests. */
	key: string
	label: string
	/** Existing route. Must reference a real current route; never invent one. */
	href: string
	status: Uiv2NavStatus
	/** Short note shown in shell context (e.g. why MIGRATE_LATER). */
	note?: string
}

export interface Uiv2NavSection {
	id: Uiv2SectionId
	label: string
	items: Uiv2NavItem[]
}

export const UIV2_NAV_SECTIONS: Uiv2NavSection[] = [
	{
		id: 'home',
		label: '首页',
		items: [
			{ key: 'home', label: '首页', href: '/', status: 'KEEP' },
			{
				key: 'dashboard',
				label: '学习概览',
				href: '/manage/dashboard',
				status: 'REFACTOR',
				note: '整页重写须另行批准；V2 仅 IA 占位',
			},
		],
	},
	{
		id: 'learn',
		label: '学习',
		items: [
			{
				key: 'today',
				label: '今日任务',
				href: '/manage/dashboard',
				status: 'MIGRATE_LATER',
				note: '统一任务流缺失（GAP-001），真实集成 BLOCKED',
			},
			{ key: 'questions', label: '题库', href: '/manage/questions', status: 'KEEP' },
			{
				key: 'mistakes',
				label: '错题',
				href: '/manage/mistakes',
				status: 'REFACTOR',
				note: '公共读 visibility cutover 归 Week3，本轨不动',
			},
			{
				key: 'review',
				label: '复习',
				href: '/manage/review',
				status: 'MIGRATE_LATER',
				note: '等 Week2 Review 切片；真实集成 BLOCKED_BY_WEEK2',
			},
		],
	},
	{
		id: 'knowledge',
		label: '知识',
		items: [
			{ key: 'subjects', label: '科目', href: '/manage/subjects', status: 'KEEP' },
			{
				key: 'knowledge-points',
				label: '知识点',
				href: '/manage/knowledge-points',
				status: 'KEEP',
			},
			{
				key: 'notes',
				label: '笔记',
				href: '/manage/notes',
				status: 'REFACTOR',
				note: '双入口（/notes + /manage/notes）收敛候选，需批准',
			},
			{ key: 'drafts', label: '草稿', href: '/manage/drafts', status: 'KEEP' },
		],
	},
	{
		id: 'analytics',
		label: '分析',
		items: [
			{
				key: 'analytics',
				label: '掌握度 · 薄弱点 · 趋势',
				href: '/manage/analytics',
				status: 'MIGRATE_LATER',
				note: '等 canonical 数据（GAP-002/003）；缺数据诚实空态',
			},
			{ key: 'search', label: '全局搜索', href: '/manage/search', status: 'KEEP' },
		],
	},
	{
		id: 'resources',
		label: '资料',
		items: [
			{ key: 'attachments', label: '附件', href: '/manage/attachments', status: 'KEEP' },
			{
				key: 'capture',
				label: '采集',
				href: '/manage/capture',
				status: 'KEEP',
				note: '失败路径 UI 归 Week2 PR-14，本轨不动',
			},
			{
				key: 'ai',
				label: 'AI',
				href: '/manage/ai',
				status: 'MIGRATE_LATER',
				note: '等 AI 纪律（PR-19）',
			},
			{ key: 'jobs', label: '任务', href: '/manage/jobs', status: 'KEEP' },
		],
	},
	{
		id: 'settings',
		label: '设置',
		items: [{ key: 'settings', label: '设置', href: '/manage/settings', status: 'KEEP' }],
	},
]

/** Flattened lookup: href -> { section, item }. First match wins. */
export function findNavEntry(href: string): {
	section: Uiv2NavSection
	item: Uiv2NavItem
} | null {
	for (const section of UIV2_NAV_SECTIONS) {
		const item = section.items.find(entry => entry.href === href)
		if (item) return { section, item }
	}
	return null
}
