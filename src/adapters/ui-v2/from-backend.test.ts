import { describe, expect, it } from 'vitest'
import { adaptMasteryScore, adaptReviewTask } from './from-backend'

describe('adaptReviewTask', () => {
	it('maps a complete backend DTO with source backend', () => {
		expect(
			adaptReviewTask({ id: 'r1', title: '函数单调性', subject: '数学', due_at: '2026-09-14' }),
		).toEqual({
			id: 'r1',
			title: '函数单调性',
			subject: '数学',
			dueAt: '2026-09-14',
			priority: 'medium',
			status: 'pending',
			source: 'backend',
		})
	})

	it('falls back to estimated with placeholder text when fields are missing', () => {
		const task = adaptReviewTask({})
		expect(task.source).toBe('estimated')
		expect(task.id).toBe('unknown')
		expect(task.title).toBe('未知任务')
		expect(task.subject).toBe('未知科目')
		expect(task.dueAt).toBeUndefined()
	})

	it('never fabricates: non-string fields become estimated, not guessed values', () => {
		const task = adaptReviewTask({ id: 42, title: null, subject: ['数学'], due_at: 20260914 })
		expect(task.source).toBe('estimated')
		expect(task.title).toBe('未知任务')
	})
})

describe('adaptMasteryScore', () => {
	it('passes through a finite backend number with low confidence', () => {
		expect(adaptMasteryScore(72)).toEqual({ value: 72, confidence: 'low', source: 'backend' })
	})

	it('returns null value for missing or non-numeric input (UI shows 暂无足够数据）)', () => {
		for (const raw of [undefined, null, 'high', NaN, Infinity]) {
			expect(adaptMasteryScore(raw)).toEqual({ value: null, confidence: 'low', source: 'estimated' })
		}
	})
})
