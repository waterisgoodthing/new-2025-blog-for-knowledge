import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { DashboardOverview, firstActionReasonText, getWelcomeGreeting } from './dashboard-overview'

const summary: DashboardSummary = {
	generated_at: '2026-07-19T10:00:00Z',
	counts: {
		questions: 12,
		mistakes: 5,
		knowledge_points: 8,
		attachments: 3,
		due_reviews: 2
	},
	recent_questions: [
		{
			id: 'question-1',
			title: '极限练习',
			question_text: '求这个函数的极限',
			updated_at: '2026-07-19T09:00:00Z'
		}
	],
	recent_mistakes: [
		{
			id: 'mistake-1',
			title: null,
			question_text: '链表删除节点',
			reason_category: 'concept',
			updated_at: '2026-07-19T08:00:00Z'
		}
	],
	recent_reviews: [
		{
			id: 'review-1',
			review_item_id: 'item-1',
			rating: 4,
			reviewed_at: '2026-07-19T07:00:00Z',
			question_text: '概率计算'
		}
	],
	sections: {
		learning: 'ready',
		activity: 'ready',
		storage: 'ready'
	},
	system: {
		service: 'ok',
		database: 'ok',
		storage: 'ok'
	},
	review_today_count: 2,
	practice_today_count: 3,
	weak_top3: [
		{
			knowledge_point_id: 7,
			name: '导数',
			attempt_count: 9,
			wrong_rate: 0.5,
			lapse_count: 4,
			due_count: 6
		}
	],
	recently_mastered_4: [
		{
			review_item_id: 'item-mastered-1',
			mistake_id: 'mistake-mastered-1',
			question_text: '矩阵特征值已经掌握',
			mastered_at: '2026-07-19T06:00:00Z'
		}
	],
	today_first_action: {
		kind: 'review',
		count: 2,
		target_route: '/manage/review',
		reason: 'due_reviews_first'
	},
	section_actions: {
		review: {
			section: 'review',
			count: 2,
			available: true,
			target_route: '/manage/review',
			reason: 'due_reviews_pending'
		},
		practice: {
			section: 'practice',
			count: 3,
			available: true,
			target_route: '/manage/practice',
			reason: 'practice_available'
		}
	}
}

describe('DashboardOverview', () => {
	it('uses the private timezone for the administrator welcome area', () => {
		expect(getWelcomeGreeting({ display_name: 'I5 Owner', timezone: 'UTC' }, new Date('2026-07-22T08:00:00Z'))).toBe('早上好，I5 Owner')
	})

	it('answers the three canonical questions from the summary contract', () => {
		render(<DashboardOverview summary={summary} />)

		expect(screen.getByRole('heading', { name: '学习管理首页' })).toBeInTheDocument()
		expect(screen.getByText('今日复习')).toBeInTheDocument()
		expect(screen.getByText('今日练习')).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '薄弱知识点 Top 3' })).toBeInTheDocument()
		expect(screen.getByText('导数')).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '最近掌握' })).toBeInTheDocument()
		expect(screen.getByText('矩阵特征值已经掌握')).toBeInTheDocument()
		expect(screen.getByText('题目')).toBeInTheDocument()
		expect(screen.getByText('最近复习')).toBeInTheDocument()
		expect(screen.getByText('服务正常')).toBeInTheDocument()
		expect(screen.queryByText(/Coming Soon|No API connected|Static shell/i)).not.toBeInTheDocument()
	})

	it('offers real daily actions without creating a parallel workspace route', () => {
		render(<DashboardOverview summary={summary} />)

		expect(screen.getByRole('heading', { name: '快速开始' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '写笔记' })).toHaveAttribute('href', '/manage/notes/new?type=note')
		expect(screen.getByRole('link', { name: '写博客' })).toHaveAttribute('href', '/manage/notes/new?type=blog')
		expect(screen.getByRole('link', { name: '图片采集' })).toHaveAttribute('href', '/manage/capture')
		expect(screen.getByRole('link', { name: '开始复习' })).toHaveAttribute('href', '/manage/review')

		const hrefs = screen.getAllByRole('link').map(link => link.getAttribute('href'))
		expect(hrefs.some(href => href?.startsWith('/workspace'))).toBe(false)
	})

	it('renders dashboard sections in preference order and omits hidden sections', () => {
		render(
			<DashboardOverview
				summary={summary}
				profile={{
					id: 'profile-1',
					user_id: 'user-1',
					display_name: 'I5 Owner',
					identity_title: 'Learner',
					signature: '',
					welcome_message: '',
					timezone: 'UTC',
					home_preferences: {
						show_welcome: false,
						section_order: ['activity', 'today', 'storage', 'stats'],
						hidden_sections: ['stats']
					}
				}}
			/>
		)

		const headings = Array.from(document.querySelectorAll('section[data-dashboard-section] h2')).map(node => node.textContent)
		expect(headings).toEqual(['最近活动', '今日任务', '系统状态'])
		expect(screen.queryByRole('heading', { name: '内容统计' })).not.toBeInTheDocument()
	})

	it('prioritises due reviews when the deterministic first action is review-first', () => {
		render(<DashboardOverview summary={summary} />)

		expect(screen.getByRole('heading', { name: '完成 2 项到期复习' })).toBeInTheDocument()
		expect(screen.getByText(firstActionReasonText('due_reviews_first'))).toBeInTheDocument()
		const primary = screen.getByRole('link', { name: '今日先做：开始复习' })
		expect(primary).toHaveAttribute('href', '/manage/review')
		expect(screen.getByRole('link', { name: '进入练习' })).toHaveAttribute('href', '/manage/practice')
	})

	it('falls back to practice-first when nothing is due for review', () => {
		render(
			<DashboardOverview
				summary={{
					...summary,
					review_today_count: 0,
					practice_today_count: 4,
					section_actions: {
						review: { ...summary.section_actions.review, count: 0, reason: 'no_due_reviews' },
						practice: { ...summary.section_actions.practice, count: 4, reason: 'practice_available' }
					},
					today_first_action: { kind: 'practice', count: 4, target_route: '/manage/practice', reason: 'practice_first_no_due_reviews' }
				}}
			/>
		)

		expect(screen.getByRole('heading', { name: '完成 4 道今日练习' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '今日先做：开始练习' })).toHaveAttribute('href', '/manage/practice')
		expect(screen.getByText('今日无到期复习')).toBeInTheDocument()
	})

	it('is honest when review, practice and mastery are all empty', () => {
		render(
			<DashboardOverview
				summary={{
					...summary,
					review_today_count: 0,
					practice_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					section_actions: {
						review: { ...summary.section_actions.review, count: 0, reason: 'no_due_reviews' },
						practice: { ...summary.section_actions.practice, count: 0, reason: 'no_eligible_practice' }
					},
					today_first_action: { kind: 'none', count: 0, target_route: null, reason: 'nothing_scheduled' }
				}}
			/>
		)

		expect(screen.getByRole('heading', { name: '今天没有安排' })).toBeInTheDocument()
		expect(screen.getByText('今日无到期复习')).toBeInTheDocument()
		expect(screen.getByText('今日暂无合适练习')).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '暂无薄弱知识点' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '暂无最近掌握' })).toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始复习' })).not.toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始练习' })).not.toBeInTheDocument()
	})

	it('degrades only the unavailable learning modules without hiding practice', () => {
		const retry = vi.fn()
		render(
			<DashboardOverview
				summary={{
					...summary,
					sections: { ...summary.sections, learning: 'unavailable' },
					system: { ...summary.system, database: 'unavailable' },
					review_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					section_actions: {
						review: { ...summary.section_actions.review, count: 0, available: false, reason: 'review_data_unavailable' },
						practice: summary.section_actions.practice
					},
					today_first_action: { kind: 'practice', count: 3, target_route: '/manage/practice', reason: 'practice_first_no_due_reviews' }
				}}
				onSummaryRetry={retry}
			/>
		)

		expect(screen.getByRole('heading', { name: '复习数据暂不可用' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '薄弱知识点暂不可用' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '最近掌握暂不可用' })).toBeInTheDocument()
		expect(screen.getByText('今日练习')).toBeInTheDocument()
		expect(screen.getByText('数据库状态未知')).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '今日先做：开始练习' })).toHaveAttribute('href', '/manage/practice')
	})

	it('is honest and offers retry when both learning and practice data are unavailable', () => {
		const retry = vi.fn()
		render(
			<DashboardOverview
				summary={{
					...summary,
					sections: { ...summary.sections, learning: 'unavailable' },
					system: { ...summary.system, database: 'unavailable' },
					review_today_count: 0,
					practice_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					section_actions: {
						review: { ...summary.section_actions.review, count: 0, available: false, reason: 'review_data_unavailable' },
						practice: { ...summary.section_actions.practice, count: 0, available: false, reason: 'practice_data_unavailable' }
					},
					today_first_action: { kind: 'none', count: 0, target_route: null, reason: 'nothing_scheduled' }
				}}
				onSummaryRetry={retry}
			/>
		)

		expect(screen.getByRole('heading', { name: '今日安排暂不可用' })).toBeInTheDocument()
		expect(screen.getByText('复习数据暂不可用')).toBeInTheDocument()
		expect(screen.getByText('练习数据暂不可用')).toBeInTheDocument()
		expect(screen.getByText('数据库状态未知')).toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始复习' })).not.toBeInTheDocument()

		const retryButtons = screen.getAllByRole('button', { name: '重新尝试' })
		expect(retryButtons.length).toBeGreaterThan(0)
		fireEvent.click(retryButtons[0])
		expect(retry).toHaveBeenCalledOnce()
	})

	it('shows independent activity failure and unknown storage without hiding learning', () => {
		const partialSummary = {
			...summary,
			sections: { learning: 'ready', activity: 'unavailable', storage: 'unknown' },
			system: { ...summary.system, storage: 'unknown' }
		} as DashboardSummary

		render(<DashboardOverview summary={partialSummary} />)

		expect(screen.getByText('最近活动暂不可用')).toBeInTheDocument()
		expect(screen.getByText('附件存储状态未知')).toBeInTheDocument()
		expect(screen.getByText('今日复习')).toBeInTheDocument()
	})

	it('treats empty storage as healthy while showing the empty label', () => {
		render(
			<DashboardOverview
				summary={{
					...summary,
					sections: { ...summary.sections, storage: 'empty' },
					system: { ...summary.system, storage: 'ok' }
				}}
			/>
		)

		expect(screen.getByText('暂无附件')).toBeInTheDocument()
		expect(screen.getByText('服务正常')).toBeInTheDocument()
	})

	it('keeps the I4 dashboard usable when private profile data is unavailable', () => {
		const retry = vi.fn()
		render(<DashboardOverview summary={summary} profileUnavailable onProfileRetry={retry} />)

		expect(screen.getByRole('heading', { name: '个人资料暂不可用' })).toBeInTheDocument()
		fireEvent.click(screen.getByRole('button', { name: '重新加载个人资料' }))
		expect(retry).toHaveBeenCalledOnce()
		expect(screen.getByText('今日复习')).toBeInTheDocument()
	})
})
