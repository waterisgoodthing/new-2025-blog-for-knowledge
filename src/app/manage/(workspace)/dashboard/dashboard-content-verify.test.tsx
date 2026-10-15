/**
 * PR-11 independent verification: dashboard client retry/focus.
 *
 * Kept in its own file so the SWR/admin-profile module mocks do not leak into
 * the pure DashboardOverview matrix in `dashboard-verify.test.tsx`.
 */
import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { DashboardSummary } from '@/lib/api/dashboard'

const mutate = vi.fn()
let swrState: { data?: unknown; error?: unknown; isLoading: boolean; mutate: typeof mutate }

vi.mock('swr', () => ({
	default: (key: string) =>
		key === 'manage-admin-profile' ? { data: undefined, error: undefined, isLoading: false, mutate: vi.fn() } : swrState
}))
vi.mock('@/lib/api/admin-profile', async importOriginal => {
	const actual = await importOriginal<typeof import('@/lib/api/admin-profile')>()
	return { ...actual, getAdminProfile: vi.fn() }
})
vi.mock('@/lib/api/dashboard', () => ({ getDashboardSummary: vi.fn() }))

const emptyish: DashboardSummary = {
	generated_at: '2026-09-25T10:00:00Z',
	counts: { questions: 0, mistakes: 0, knowledge_points: 0, attachments: 0, due_reviews: 0 },
	recent_questions: [],
	recent_mistakes: [],
	recent_reviews: [],
	sections: { learning: 'empty', activity: 'empty', storage: 'empty' },
	system: { service: 'ok', database: 'ok', storage: 'ok' },
	review_today_count: 0,
	practice_today_count: 0,
	weak_top3: [],
	recently_mastered_4: [],
	today_first_action: { kind: 'none', count: 0, target_route: null, reason: 'nothing_scheduled' },
	section_actions: {
		review: { section: 'review', count: 0, available: true, target_route: '/manage/review', reason: 'no_due_reviews' },
		practice: { section: 'practice', count: 0, available: true, target_route: '/manage/practice', reason: 'no_eligible_practice' }
	}
}

describe('PR-11 verify: DashboardContent retry refocuses result region', () => {
	beforeEach(() => {
		mutate.mockReset()
	})

	it('retries then moves focus to the result region when data arrives', async () => {
		swrState = { isLoading: false, error: new Error('offline'), mutate }
		const { DashboardContent } = await import('./dashboard-content')
		const { rerender } = render(<DashboardContent />)

		fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))
		expect(mutate).toHaveBeenCalledOnce()

		swrState = { isLoading: false, data: emptyish, mutate }
		rerender(<DashboardContent />)

		expect(await screen.findByRole('region', { name: '学习概览结果' })).toHaveFocus()
	})
})
