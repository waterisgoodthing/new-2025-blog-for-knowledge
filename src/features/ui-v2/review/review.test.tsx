import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { adaptReviewItem } from '../../../adapters/ui-v2/from-backend'
import {
	mockReviewV2Empty,
	mockReviewV2Error,
	mockReviewV2Loading,
	mockReviewV2Normal,
	mockReviewV2Partial,
} from '../../../mocks/ui-v2/review-v2'
import { Uiv2ReviewSection } from './ReviewSection'
import { useReviewQueueModel } from './useReviewQueueModel'

describe('Uiv2ReviewSection', () => {
	it('renders queue items with text-first due state and no invented rating UI', () => {
		render(<Uiv2ReviewSection model={mockReviewV2Normal} />)
		expect(screen.getByRole('heading', { name: '复习' })).toBeInTheDocument()
		expect(screen.getByText('Mock：函数单调性错题')).toBeInTheDocument()
		expect(screen.getByText('已逾期')).toBeInTheDocument()
		expect(screen.getByText('暂无题干摘要')).toBeInTheDocument()
		expect(screen.getByText('数据来源：示例数据')).toBeInTheDocument()
		// no rating scale invented by the UI
		expect(screen.queryByRole('radiogroup')).not.toBeInTheDocument()
		expect(screen.queryByText(/评分/)).not.toBeInTheDocument()
	})

	it('marks items without reviewable content honestly', () => {
		render(<Uiv2ReviewSection model={mockReviewV2Normal} />)
		expect(screen.getByText('该复习项暂无可作答内容（等待 Week2 契约）')).toBeInTheDocument()
		expect(screen.getAllByRole('link', { name: '开始本次复习' })).toHaveLength(1)
	})

	it('covers loading / empty / error / partial states', () => {
		const { rerender } = render(<Uiv2ReviewSection model={mockReviewV2Loading} />)
		expect(screen.getByRole('status', { name: '正在加载复习队列' })).toBeInTheDocument()

		rerender(<Uiv2ReviewSection model={mockReviewV2Empty} />)
		expect(
			screen.getByText('复习队列是空的。确认错题后，到期的复习会出现在这里。'),
		).toBeInTheDocument()

		rerender(<Uiv2ReviewSection model={mockReviewV2Error} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 复习队列加载失败，请重试')

		rerender(<Uiv2ReviewSection model={mockReviewV2Partial} />)
		expect(screen.getAllByRole('note')[0]).toHaveTextContent('部分数据加载成功')
	})
})

describe('adaptReviewItem + useReviewQueueModel (T-U5-3)', () => {
	it('adapts the canonical DTO without inventing rating semantics', () => {
		const item = adaptReviewItem(
			{
				id: 'ri-1',
				target_type: 'mistake',
				target_id: 'm-1',
				state: 'active',
				algorithm: 'fixed_interval_v2',
				interval_days: 1,
				repetitions: 0,
				next_review_at: '2020-01-01T00:00:00+00:00',
				last_reviewed_at: null,
				last_rating: 1,
				question_text: '单调性错题',
				mistake_reason: null,
			},
			new Date('2026-09-20T00:00:00+00:00'),
		)
		expect(item.task).toMatchObject({
			id: 'ri-1',
			title: '单调性错题',
			subject: '未知科目',
			priority: 'high',
			status: 'overdue',
			source: 'backend',
		})
		expect(item.questionExcerpt).toBe('单调性错题')
		expect(item.hasReviewTarget).toBe(true)
	})

	it('marks future-due items pending without inventing subjects', () => {
		const item = adaptReviewItem(
			{
				id: 'ri-2',
				target_type: 'mistake',
				target_id: 'm-2',
				state: 'active',
				algorithm: 'fixed_interval_v2',
				interval_days: 7,
				repetitions: 2,
				next_review_at: '2030-01-01T00:00:00+00:00',
				last_reviewed_at: null,
				last_rating: 4,
				question_text: '几何题',
				mistake_reason: null,
			},
			new Date('2026-09-20T00:00:00+00:00'),
		)
		expect(item.task).toMatchObject({ status: 'pending', priority: 'medium', subject: '未知科目' })
	})

	it('moves loading -> ready through the real client shape', async () => {
		const fetchQueue = vi.fn().mockResolvedValue([
			{
				id: 'ri-1',
				target_type: 'mistake',
				target_id: 'm-1',
				state: 'active',
				algorithm: 'fixed_interval_v2',
				interval_days: 3,
				repetitions: 2,
				next_review_at: '2026-09-20T00:00:00+00:00',
				last_reviewed_at: null,
				last_rating: 4,
				question_text: '单调性错题',
				mistake_reason: null,
			},
		])
		function Probe() {
			const { model } = useReviewQueueModel({ fetchQueue })
			return <span data-testid="rq">{`${model.state}:${model.source}:${model.data?.items.length ?? 0}`}</span>
		}
		render(<Probe />)
		await waitFor(() => expect(screen.getByTestId('rq')).toHaveTextContent('ready:backend:1'))
	})
})
