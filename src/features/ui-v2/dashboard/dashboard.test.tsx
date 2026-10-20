import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { adaptDashboardSummary } from '../../../adapters/ui-v2/from-backend'
import type { DashboardSummary } from '../../../lib/api/dashboard'
import {
	mockDashboardV2Empty,
	mockDashboardV2Error,
	mockDashboardV2Loading,
	mockDashboardV2Normal,
	mockDashboardV2NoData,
	mockDashboardV2Partial,
} from '../../../mocks/ui-v2/dashboard-v2'
import { Uiv2DashboardSection } from './DashboardSection'
import { useDashboardModel } from './useDashboardModel'

function summary(overrides: Partial<DashboardSummary> = {}): DashboardSummary {
	return {
		generated_at: '2026-09-15T00:00:00Z',
		counts: { questions: 10, mistakes: 4, knowledge_points: 6, attachments: 2, due_reviews: 3 },
		recent_questions: [
			{ id: 'q1', title: '单调性', question_text: '求单调区间', updated_at: '2026-09-15' },
		],
		recent_mistakes: [],
		recent_reviews: [],
		sections: { learning: 'ready', activity: 'ready', storage: 'ok' },
		system: { service: 'ok', database: 'ok', storage: 'ok' },
		...overrides,
	}
}

describe('adaptDashboardSummary', () => {
	it('maps counts and recents, leaving weakness/trend honestly empty', () => {
		const model = adaptDashboardSummary(summary())
		expect(model.today.dueCount).toBe(3)
		expect(model.review.dueTodayCount).toBe(3)
		expect(model.weaknesses).toEqual([])
		expect(model.trend).toEqual([])
		expect(model.recent).toHaveLength(1)
		expect(model.recent[0]).toMatchObject({ kind: 'question', source: 'backend' })
		expect(model.nextAction).toMatchObject({ href: '/manage/review', source: 'backend' })
		expect(model.source).toBe('backend')
	})

	it('degrades unavailable sections to null + estimated without fabricating', () => {
		const model = adaptDashboardSummary(
			summary({ sections: { learning: 'unavailable', activity: 'empty', storage: 'unknown' } }),
		)
		expect(model.today.dueCount).toBeNull()
		expect(model.today.source).toBe('estimated')
		expect(model.recent).toEqual([])
		expect(model.nextAction).toBeNull()
	})

	it('yields no next action when nothing is due', () => {
		const model = adaptDashboardSummary(
			summary({ counts: { questions: 1, mistakes: 0, knowledge_points: 0, attachments: 0, due_reviews: 0 } }),
		)
		expect(model.nextAction).toBeNull()
	})
})

describe('Uiv2DashboardSection', () => {
	it('renders all six learning blocks in success state', () => {
		render(<Uiv2DashboardSection model={mockDashboardV2Normal} />)
		expect(screen.getByText('今日学习')).toBeInTheDocument()
		expect(screen.getByText('今日任务')).toBeInTheDocument()
		// M1: provenance is surfaced, never silent
		expect(screen.getByText('数据来源：示例数据')).toBeInTheDocument()
		expect(screen.getByText('复习')).toBeInTheDocument()
		expect(screen.getByText('薄弱点')).toBeInTheDocument()
		expect(screen.getByText('最近学习')).toBeInTheDocument()
		expect(screen.getByText('学习趋势')).toBeInTheDocument()
		expect(screen.getByText('处理到期复习')).toBeInTheDocument()
	})

	it('renders honest no-data copy when values are null', () => {
		render(<Uiv2DashboardSection model={mockDashboardV2NoData} />)
		expect(screen.getAllByText('暂无足够数据').length).toBeGreaterThan(0)
		expect(screen.getByText('数据积累中')).toBeInTheDocument()
	})

	it('covers loading / empty / error / partial states', () => {
		const { rerender } = render(<Uiv2DashboardSection model={mockDashboardV2Loading} />)
		expect(screen.getByRole('status', { name: '正在加载仪表盘' })).toBeInTheDocument()

		rerender(<Uiv2DashboardSection model={mockDashboardV2Empty} />)
		expect(screen.getByText('还没有学习数据，先去题库做几道题吧')).toBeInTheDocument()

		rerender(<Uiv2DashboardSection model={mockDashboardV2Error} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 仪表盘加载失败，请重试')

		rerender(<Uiv2DashboardSection model={mockDashboardV2Partial} />)
		expect(screen.getByRole('note')).toHaveTextContent('部分数据加载成功')
	})
})

describe('useDashboardModel', () => {
	it('transitions loading -> ready and supports retry after failure', async () => {
		const fetchSummary = vi
			.fn()
			.mockRejectedValueOnce(new Error('unauthorized'))
			.mockResolvedValueOnce(summary())

		function Probe() {
			const { model, refresh } = useDashboardModel({ fetchSummary })
			return (
				<div>
					<span data-testid="state">{model.state}</span>
					<button type="button" onClick={() => void refresh()}>
						refresh
					</button>
				</div>
			)
		}
		render(<Probe />)
		await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error'))

		screen.getByRole('button', { name: 'refresh' }).click()
		await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('ready'))
		expect(fetchSummary).toHaveBeenCalledTimes(2)
	})
})
