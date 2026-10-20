/**
 * PR-11 independent verification matrix (author: PR-11-verify, senior-qa-sdet).
 *
 * Written without reusing the implementer's component tests. Asserts the
 * accepted dashboard contract end to end at the component boundary:
 * review-first / practice-first / all-empty / partial failure / retry-focus,
 * the four async states, and reduced-motion safety.
 */
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { AsyncStatePanel } from '@/components/async-state-panel'
import { DashboardOverview } from './dashboard-overview'

function summary(overrides: Partial<DashboardSummary> = {}): DashboardSummary {
	return {
		generated_at: '2026-09-25T10:00:00Z',
		counts: { questions: 6, mistakes: 4, knowledge_points: 4, attachments: 0, due_reviews: 2 },
		recent_questions: [],
		recent_mistakes: [],
		recent_reviews: [],
		sections: { learning: 'ready', activity: 'ready', storage: 'empty' },
		system: { service: 'ok', database: 'ok', storage: 'ok' },
		review_today_count: 2,
		practice_today_count: 3,
		weak_top3: [
			{ knowledge_point_id: 6, name: 'PR11V Alpha', attempt_count: 2, wrong_rate: 1, lapse_count: 2, due_count: 1 },
			{ knowledge_point_id: 7, name: 'PR11V Beta', attempt_count: 2, wrong_rate: 0.5, lapse_count: 0, due_count: 0 },
			{ knowledge_point_id: 8, name: 'PR11V Gamma', attempt_count: 1, wrong_rate: 0, lapse_count: 0, due_count: 1 }
		],
		recently_mastered_4: [
			{ review_item_id: 'i6', mistake_id: 'm6', question_text: 'PR11V mastered item', mastered_at: '2026-09-25T09:30:00Z' }
		],
		today_first_action: { kind: 'review', count: 2, target_route: '/manage/review', reason: 'due_reviews_first' },
		section_actions: {
			review: { section: 'review', count: 2, available: true, target_route: '/manage/review', reason: 'due_reviews_pending' },
			practice: { section: 'practice', count: 3, available: true, target_route: '/manage/practice', reason: 'practice_available' }
		},
		...overrides
	}
}

describe('PR-11 verify: dashboard three questions', () => {
	it('review-first: due reviews drive the first action and all three answers render', () => {
		render(<DashboardOverview summary={summary()} />)

		expect(screen.getByRole('heading', { name: '完成 2 项到期复习' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '今日先做：开始复习' })).toHaveAttribute('href', '/manage/review')
		expect(screen.getByText('2')).toBeInTheDocument()
		expect(screen.getByText('3')).toBeInTheDocument()
		expect(screen.getByText('PR11V Alpha')).toBeInTheDocument()
		expect(screen.getByText('错误率 100% · 作答 2 · 遗忘 2 · 到期 1')).toBeInTheDocument()
		expect(screen.getByText('PR11V mastered item')).toBeInTheDocument()
	})

	it('practice-first: no due reviews -> no review entry, practice CTA instead', () => {
		render(
			<DashboardOverview
				summary={summary({
					review_today_count: 0,
					today_first_action: { kind: 'practice', count: 3, target_route: '/manage/practice', reason: 'practice_first_no_due_reviews' },
					section_actions: {
						review: { section: 'review', count: 0, available: true, target_route: '/manage/review', reason: 'no_due_reviews' },
						practice: { section: 'practice', count: 3, available: true, target_route: '/manage/practice', reason: 'practice_available' }
					}
				})}
			/>
		)

		expect(screen.getByRole('heading', { name: '完成 3 道今日练习' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '今日先做：开始练习' })).toHaveAttribute('href', '/manage/practice')
		expect(screen.getByRole('heading', { name: '今日无到期复习' })).toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始复习' })).not.toBeInTheDocument()
	})

	it('all-empty: gives no false entry point and states the emptiness honestly', () => {
		render(
			<DashboardOverview
				summary={summary({
					review_today_count: 0,
					practice_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					today_first_action: { kind: 'none', count: 0, target_route: null, reason: 'nothing_scheduled' },
					section_actions: {
						review: { section: 'review', count: 0, available: true, target_route: '/manage/review', reason: 'no_due_reviews' },
						practice: { section: 'practice', count: 0, available: true, target_route: '/manage/practice', reason: 'no_eligible_practice' }
					}
				})}
			/>
		)

		expect(screen.getByRole('heading', { name: '今天没有安排' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '今日无到期复习' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '今日暂无合适练习' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '暂无薄弱知识点' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '暂无最近掌握' })).toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始复习' })).not.toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始练习' })).not.toBeInTheDocument()
	})

	it('partial failure: review/weak/mastered degrade but practice stays actionable with retry', () => {
		const retry = vi.fn()
		render(
			<DashboardOverview
				summary={summary({
					sections: { learning: 'unavailable', activity: 'ready', storage: 'empty' },
					system: { service: 'ok', database: 'unavailable', storage: 'ok' },
					review_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					today_first_action: { kind: 'practice', count: 3, target_route: '/manage/practice', reason: 'practice_first_no_due_reviews' },
					section_actions: {
						review: { section: 'review', count: 0, available: false, target_route: '/manage/review', reason: 'review_data_unavailable' },
						practice: { section: 'practice', count: 3, available: true, target_route: '/manage/practice', reason: 'practice_available' }
					}
				})}
				onSummaryRetry={retry}
			/>
		)

		expect(screen.getByRole('heading', { name: '复习数据暂不可用' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '薄弱知识点暂不可用' })).toBeInTheDocument()
		expect(screen.getByRole('heading', { name: '最近掌握暂不可用' })).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '今日先做：开始练习' })).toHaveAttribute('href', '/manage/practice')
		expect(screen.getByText('数据库状态未知')).toBeInTheDocument()

		fireEvent.click(screen.getAllByRole('button', { name: '重新尝试' })[0])
		expect(retry).toHaveBeenCalledOnce()
	})

	it('total failure: both sections unavailable -> honest banner + retry, no CTA', () => {
		const retry = vi.fn()
		render(
			<DashboardOverview
				summary={summary({
					sections: { learning: 'unavailable', activity: 'unavailable', storage: 'unknown' },
					system: { service: 'ok', database: 'unavailable', storage: 'unknown' },
					review_today_count: 0,
					practice_today_count: 0,
					weak_top3: [],
					recently_mastered_4: [],
					today_first_action: { kind: 'none', count: 0, target_route: null, reason: 'nothing_scheduled' },
					section_actions: {
						review: { section: 'review', count: 0, available: false, target_route: '/manage/review', reason: 'review_data_unavailable' },
						practice: { section: 'practice', count: 0, available: false, target_route: '/manage/practice', reason: 'practice_data_unavailable' }
					}
				})}
				onSummaryRetry={retry}
			/>
		)

		expect(screen.getByRole('heading', { name: '今日安排暂不可用' })).toBeInTheDocument()
		expect(screen.getByText('复习数据暂不可用')).toBeInTheDocument()
		expect(screen.getByText('练习数据暂不可用')).toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始复习' })).not.toBeInTheDocument()
		expect(screen.queryByRole('link', { name: '今日先做：开始练习' })).not.toBeInTheDocument()
	})
})

describe('PR-11 verify: four async states + reduced motion', () => {
	it('loading state marks its skeleton animatable but static under reduced motion', () => {
		render(<AsyncStatePanel status='loading' loadingLabel='正在加载学习概览' skeletonRows={3} />)
		expect(screen.getByRole('status', { name: '正在加载学习概览' })).toBeInTheDocument()
		const skeletons = screen.getAllByTestId('async-state-panel-skeleton')
		expect(skeletons).toHaveLength(3)
		expect(skeletons[0].className).toContain('animate-pulse')
		expect(skeletons[0].className).toContain('motion-reduce:animate-none')
	})

	it('empty and error states expose the expected semantics', () => {
		const { rerender } = render(<AsyncStatePanel status='empty' title='暂无内容' emptyHint='没有数据' />)
		expect(screen.getByRole('heading', { name: '暂无内容' })).toBeInTheDocument()
		rerender(<AsyncStatePanel status='error' title='加载失败' error='offline' onRetry={() => {}} retryLabel='重新尝试' />)
		expect(screen.getByRole('alert')).toHaveTextContent('offline')
		expect(screen.getByRole('button', { name: '重新尝试' })).toBeInTheDocument()
	})
})


