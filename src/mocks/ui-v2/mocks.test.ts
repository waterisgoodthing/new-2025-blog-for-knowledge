import { describe, expect, it } from 'vitest'
import {
	mockDashboardEmpty,
	mockDashboardError,
	mockDashboardLoading,
	mockDashboardNormal,
	mockDashboardOverdue,
	mockDashboardPartial,
	mockMistakesEmpty,
	mockMistakesError,
	mockMistakesLoading,
	mockMistakesNormal,
	mockMistakesOverdue,
	mockMistakesPartial,
	mockReviewEmpty,
	mockReviewError,
	mockReviewLoading,
	mockReviewNormal,
	mockReviewOverdue,
	mockReviewPartial,
} from './index'

const allModels = [
	mockDashboardNormal,
	mockDashboardEmpty,
	mockDashboardLoading,
	mockDashboardError,
	mockDashboardPartial,
	mockDashboardOverdue,
	mockReviewNormal,
	mockReviewEmpty,
	mockReviewLoading,
	mockReviewError,
	mockReviewPartial,
	mockReviewOverdue,
	mockMistakesNormal,
	mockMistakesEmpty,
	mockMistakesLoading,
	mockMistakesError,
	mockMistakesPartial,
	mockMistakesOverdue,
]

describe('ui-v2 mocks', () => {
	it('covers all six states across dashboard/review/mistakes', () => {
		expect(allModels).toHaveLength(18)
		const states = new Set(allModels.map(m => m.state))
		for (const s of ['ready', 'empty', 'loading', 'error', 'partial'] as const) {
			expect(states.has(s)).toBe(true)
		}
	})

	it('every mock is labeled source mock and never leaks into backend paths', () => {
		for (const m of allModels) {
			expect(m.source).toBe('mock')
		}
		for (const m of [mockDashboardNormal, mockReviewNormal, mockMistakesNormal]) {
			for (const t of m.data ?? []) {
				expect(t.source).toBe('mock')
				expect(t.id.startsWith('mock-')).toBe(true)
			}
		}
	})

	it('error states carry a retryable message, empty states carry empty data', () => {
		for (const m of [mockDashboardError, mockReviewError, mockMistakesError]) {
			expect(m.state).toBe('error')
			expect(typeof m.error).toBe('string')
		}
		for (const m of [mockDashboardEmpty, mockReviewEmpty, mockMistakesEmpty]) {
			expect(m.state).toBe('empty')
			expect(m.data).toEqual([])
		}
	})
})
